import uuid

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from app.config import settings
from app.db import SessionLocal
from app.models import ResearchSession, SubQuestion, SourceDocument
from app.state import GraphState


SYNTHESIZE_PROMPT = """You are a research report writer. Write a comprehensive, well-cited Markdown report on the following topic.

Topic: {query}

Your report must be organized into sections, one per sub-question. Use inline numbered footnotes like [1], [2] etc.

At the end, include a "## Bibliography" section with entries in this format:
[N] Title - URL (accessed {access_date})

Rules:
- Every factual claim MUST have a footnote citation.
- Every footnote [N] MUST have a matching bibliography entry.
- If a claim has multiple sources, cite all of them: [1][2].
- Do NOT invent facts that are not supported by the provided sources.
- If the sources disagree, note the disagreement.

Sub-questions and their sources:

{sections}

Write the report now."""


def synthesize_node(state: GraphState) -> GraphState:
    session_id = uuid.UUID(state["session_id"])

    llm = ChatOpenAI(
        model=settings.synthesize_model,
        base_url=settings.nvidia_base_url,
        api_key=settings.nvidia_api_key,
        temperature=0.3,
    )

    db = SessionLocal()
    try:
        session = db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
        sub_questions = db.query(SubQuestion).filter(
            SubQuestion.session_id == session_id
        ).all()

        sections_parts = []
        for sq in sub_questions:
            sources = db.query(SourceDocument).filter(
                SourceDocument.sub_question_id == sq.id
            ).all()
            sources_text = "\n".join(
                f"- [{s.title}]({s.url}): {s.content_full or s.snippet}"
                for s in sources
            )
            sections_parts.append(f"### {sq.question}\nSources:\n{sources_text}")

        sections_block = "\n\n".join(sections_parts)

        response = llm.invoke([HumanMessage(
            content=SYNTHESIZE_PROMPT.format(
                query=state["query"],
                sections=sections_block,
                access_date="2026-06-24",
            )
        )])

        report = response.content.strip()
        session.report_markdown = report
        session.status = "verifying"
        db.commit()
    finally:
        db.close()

    return state
