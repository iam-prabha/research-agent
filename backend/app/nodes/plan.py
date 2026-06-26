import json
import uuid

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from app.config import settings
from app.db import SessionLocal
from app.models import ResearchSession, SubQuestion
from app.state import GraphState


PLAN_PROMPT = """You are a research planner. Given a user's research topic, decompose it into 3-6 specific sub-questions that would comprehensively cover the topic.

Rules:
- Each sub-question should be self-contained and searchable.
- Cover different facets of the topic (historical, technical, current state, controversies, etc.).
- Output ONLY a JSON array of strings, no other text.

Topic: {query}"""


def plan_node(state: GraphState) -> GraphState:
    session_id = uuid.UUID(state["session_id"])
    query = state["query"]

    llm = ChatOpenAI(
        model=settings.plan_model,
        base_url=settings.nvidia_base_url,
        api_key=settings.nvidia_api_key,
        temperature=0.3,
    )

    response = llm.invoke([HumanMessage(content=PLAN_PROMPT.format(query=query))])
    sub_questions = json.loads(response.content.strip())

    db = SessionLocal()
    try:
        session = db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
        session.status = "searching"
        for q in sub_questions:
            sq = SubQuestion(session_id=session_id, question=q, status="pending")
            db.add(sq)
        db.commit()
    finally:
        db.close()

    return {
        **state,
        "sub_questions": sub_questions,
    }
