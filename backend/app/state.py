from typing import NotRequired, TypedDict


class GraphState(TypedDict):
    session_id: str
    query: str
    sub_questions: list[str]
    search_round: int
    errors: list[str]
    unverified_claims: NotRequired[list[str]]
