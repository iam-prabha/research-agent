from langgraph.graph import StateGraph, END

from app.state import GraphState
from app.nodes.plan import plan_node
from app.nodes.search import search_node
from app.nodes.extract import extract_node
from app.nodes.synthesize import synthesize_node
from app.nodes.verify import verify_node
from app.config import settings


def needs_re_search(state: GraphState) -> str:
    unverified = state.get("unverified_claims", [])
    if unverified and state["search_round"] <= settings.max_search_rounds:
        return "search"
    return END


workflow = StateGraph(GraphState)

workflow.add_node("plan", plan_node)
workflow.add_node("search", search_node)
workflow.add_node("extract", extract_node)
workflow.add_node("synthesize", synthesize_node)
workflow.add_node("verify", verify_node)

workflow.set_entry_point("plan")
workflow.add_edge("plan", "search")
workflow.add_edge("search", "extract")
workflow.add_edge("extract", "synthesize")
workflow.add_edge("synthesize", "verify")
workflow.add_conditional_edges("verify", needs_re_search)

graph = workflow.compile()
