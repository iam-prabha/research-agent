import uuid

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from app.config import settings
from app.db import SessionLocal
from app.models import ResearchSession, ExtractedClaim, VerificationCheck, SourceDocument
from app.state import GraphState


VERIFY_PROMPT = """You are a fact-checker. Given a claim and its source document, determine if the source actually supports the claim.

Claim: "{claim}"

Source URL: {url}
Source Content: {content}

Respond with a JSON object:
{{
  "status": "confirmed" | "contradicted" | "unverifiable",
  "note": "Brief explanation of your reasoning"
}}

Output ONLY valid JSON."""


def verify_node(state: GraphState) -> GraphState:
    session_id = uuid.UUID(state["session_id"])

    llm = ChatOpenAI(
        model=settings.verify_model,
        base_url=settings.nvidia_base_url,
        api_key=settings.nvidia_api_key,
        temperature=0.2,
    )

    db = SessionLocal()
    try:
        session = db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
        claims = db.query(ExtractedClaim).filter(
            ExtractedClaim.session_id == session_id
        ).all()

        unverified = []

        for claim in claims:
            source = db.query(SourceDocument).filter(
                SourceDocument.id == claim.source_id
            ).first()
            if not source:
                continue

            try:
                response = llm.invoke([HumanMessage(
                    content=VERIFY_PROMPT.format(
                        claim=claim.text,
                        url=source.url,
                        content=source.content_full or source.snippet or "",
                    )
                )])

                import json
                result = json.loads(response.content.strip())

                check = VerificationCheck(
                    claim_id=claim.id,
                    status=result["status"],
                    note=result.get("note", ""),
                    search_round=state["search_round"],
                )
                db.add(check)
                db.commit()

                if result["status"] != "confirmed":
                    unverified.append(claim.text)
            except Exception:
                unverified.append(claim.text)

        if unverified:
            if state["search_round"] <= settings.max_search_rounds:
                session.status = "searching"
            else:
                session.status = "completed"
        else:
            session.status = "completed"
        db.commit()
    finally:
        db.close()

    return {
        **state,
        "unverified_claims": unverified,
    }
