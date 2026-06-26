import json
import uuid

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from app.config import settings
from app.db import SessionLocal
from app.models import ResearchSession, SourceDocument, ExtractedClaim
from app.state import GraphState


EXTRACT_PROMPT = """You are an information extractor. Given a source document about a research topic, extract the key factual claims and provide a brief summary.

Source URL: {url}
Source Title: {title}
Content: {content}

Output a JSON object with:
1. "claims": an array of strings, each an atomic factual statement from the source.
2. "summary": a 2-3 sentence summary of what this source contributes.

Output ONLY valid JSON, no other text."""


def extract_node(state: GraphState) -> GraphState:
    session_id = uuid.UUID(state["session_id"])

    llm = ChatOpenAI(
        model=settings.extract_model,
        base_url=settings.nvidia_base_url,
        api_key=settings.nvidia_api_key,
        temperature=0.2,
    )

    db = SessionLocal()
    try:
        session = db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
        sources = db.query(SourceDocument).filter(
            SourceDocument.session_id == session_id,
            SourceDocument.content_full.is_(None),
        ).all()

        for source in sources:
            try:
                response = llm.invoke([HumanMessage(
                    content=EXTRACT_PROMPT.format(
                        url=source.url,
                        title=source.title or "",
                        content=source.snippet or "",
                    )
                )])

                extracted = json.loads(response.content.strip())
                source.content_full = extracted.get("summary", "")
                db.commit()

                for claim_text in extracted.get("claims", []):
                    claim = ExtractedClaim(
                        session_id=session_id,
                        source_id=source.id,
                        text=claim_text,
                    )
                    db.add(claim)
                db.commit()
            except Exception:
                pass

        session.status = "synthesizing"
        db.commit()
    finally:
        db.close()

    return state
