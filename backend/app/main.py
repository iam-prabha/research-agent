import asyncio
import json
import logging
import uuid
from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from pydantic import BaseModel, Field
from pydantic import UUID4
from sse_starlette.sse import EventSourceResponse

from app.db import Base, SessionLocal, engine
from app.graph import graph
from app.models import ResearchSession
from app.state import GraphState
from app.config import settings


class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=1000)


INTERMEDIATE_STATUSES = ("planning", "searching", "extracting", "synthesizing", "verifying")


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_conn = redis.from_url(settings.redis_url)
    await FastAPILimiter.init(redis_conn)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        stale = (
            db.query(ResearchSession)
            .filter(ResearchSession.status.in_(INTERMEDIATE_STATUSES))
            .all()
        )
        for s in stale:
            s.status = "completed" if s.report_markdown else "failed"

        orphans = (
            db.query(ResearchSession)
            .filter(
                ResearchSession.status == "failed",
                ResearchSession.report_markdown.isnot(None),
            )
            .all()
        )
        for s in orphans:
            s.status = "completed"

        if stale or orphans:
            db.commit()
    finally:
        db.close()
    yield
    await redis_conn.close()


app = FastAPI(title="Research Agent", lifespan=lifespan)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


POST_LIMIT = [Depends(RateLimiter(times=10, minutes=1))]
READ_LIMIT = [Depends(RateLimiter(times=30, minutes=1))]


@app.post("/api/research", dependencies=POST_LIMIT)
async def create_research(req: ResearchRequest):
    db = SessionLocal()
    try:
        session = ResearchSession(query=req.query, status="planning")
        db.add(session)
        db.commit()
        db.refresh(session)
        return {"session_id": str(session.id)}
    finally:
        db.close()


@app.get("/api/research/history", dependencies=READ_LIMIT)
async def list_sessions():
    db = SessionLocal()
    try:
        sessions = (
            db.query(ResearchSession)
            .order_by(ResearchSession.created_at.desc())
            .limit(20)
            .all()
        )
        return [
            {
                "id": str(s.id),
                "query": s.query,
                "status": s.status,
                "has_report": s.report_markdown is not None,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in sessions
        ]
    finally:
        db.close()


@app.get("/api/research/{session_id}", dependencies=READ_LIMIT)
async def get_session(session_id: UUID4):
    db = SessionLocal()
    try:
        session = (
            db.query(ResearchSession)
            .filter(ResearchSession.id == session_id)
            .first()
        )
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return {
            "id": str(session.id),
            "query": session.query,
            "status": session.status,
            "report_markdown": session.report_markdown,
            "created_at": session.created_at.isoformat()
            if session.created_at
            else None,
        }
    finally:
        db.close()


@app.delete("/api/research/{session_id}", dependencies=READ_LIMIT)
async def delete_session(session_id: UUID4):
    db = SessionLocal()
    try:
        session = (
            db.query(ResearchSession)
            .filter(ResearchSession.id == session_id)
            .first()
        )
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        db.delete(session)
        db.commit()
        return {"deleted": True}
    finally:
        db.close()


def _run_and_push(
    session_id: str, query: str, queue: asyncio.Queue, loop: asyncio.AbstractEventLoop
) -> None:
    try:
        initial = GraphState(
            session_id=session_id,
            query=query,
            sub_questions=[],
            search_round=1,
            errors=[],
        )
        for step in graph.stream(initial):
            asyncio.run_coroutine_threadsafe(
                queue.put(("step", step)), loop
            ).result()
        asyncio.run_coroutine_threadsafe(
            queue.put(("_done", None)), loop
        ).result()
    except Exception as exc:
        logging.exception("Graph execution failed")
        asyncio.run_coroutine_threadsafe(
            queue.put(("_error", "Research execution failed")), loop
        ).result()


def _fail_session(session_id: str) -> None:
    db = SessionLocal()
    try:
        current = (
            db.query(ResearchSession)
            .filter(ResearchSession.id == uuid.UUID(session_id))
            .first()
        )
        if current is not None:
            current.status = "failed"
            db.commit()
    finally:
        db.close()


@app.get("/api/research/{session_id}/stream")
async def stream_research(session_id: UUID4):
    db = SessionLocal()
    try:
        session = (
            db.query(ResearchSession)
            .filter(ResearchSession.id == session_id)
            .first()
        )
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        query = session.query
    finally:
        db.close()

    async def event_generator():
        queue: asyncio.Queue = asyncio.Queue()

        loop = asyncio.get_event_loop()
        loop.run_in_executor(
            None,
            _run_and_push,
            str(session_id),
            query,
            queue,
            loop,
        )

        while True:
            msg_type, payload = await queue.get()

            if msg_type == "step":
                for node_name, state in payload.items():
                    yield {
                        "event": "status",
                        "data": json.dumps({"node": node_name}),
                    }
                    unverified = state.get("unverified_claims") or []
                    if unverified:
                        yield {
                            "event": "warning",
                            "data": json.dumps(
                                {
                                    "message": f"{len(unverified)} claims need re-verification",
                                }
                            ),
                        }

            elif msg_type == "_error":
                _fail_session(str(session_id))
                yield {
                    "event": "research_error",
                    "data": json.dumps({"message": payload}),
                }
                return

            elif msg_type == "_done":
                break

        db = SessionLocal()
        try:
            current = (
                db.query(ResearchSession)
                .filter(ResearchSession.id == session_id)
                .first()
            )
            if current is not None:
                if current.status in ("searching", "extracting", "synthesizing", "verifying", "planning"):
                    current.status = "completed" if current.report_markdown else "failed"
                    db.commit()
                if current.report_markdown:
                    yield {
                        "event": "done",
                        "data": json.dumps({"report": current.report_markdown}),
                    }
                else:
                    yield {
                        "event": "research_error",
                        "data": json.dumps(
                            {
                                "message": "Research completed but no report was generated",
                            }
                        ),
                    }
            else:
                yield {
                    "event": "research_error",
                    "data": json.dumps({"message": "Session not found"}),
                }
        finally:
            db.close()

    return EventSourceResponse(event_generator())
