import uuid

from tavily import TavilyClient

from app.config import settings
from app.db import SessionLocal
from app.models import ResearchSession, SourceDocument, SubQuestion
from app.state import GraphState

tavily = TavilyClient(api_key=settings.tavily_api_key)


def search_node(state: GraphState) -> GraphState:
    session_id = uuid.UUID(state["session_id"])
    search_round = state["search_round"]

    db = SessionLocal()
    try:
        session = (
            db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
        )
        sub_questions = (
            db.query(SubQuestion).filter(SubQuestion.session_id == session_id).all()
        )

        for sq in sub_questions:
            sq.status = "searching"
            db.commit()

            result = tavily.search(
                query=sq.question,
                search_depth="advanced",
                max_results=5,
            )

            for r in result.get("results", []):
                source = SourceDocument(
                    session_id=session_id,
                    sub_question_id=sq.id,
                    url=r.get("url", ""),
                    title=r.get("title", ""),
                    snippet=r.get("content", ""),
                )
                db.add(source)

            sq.status = "completed"
            db.commit()

        session.status = "extracting"
        db.commit()
    finally:
        db.close()

    return {
        **state,
        "search_round": search_round + 1,
    }
