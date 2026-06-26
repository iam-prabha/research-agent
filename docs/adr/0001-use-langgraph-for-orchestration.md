# ADR 0001: Use LangGraph for research pipeline orchestration

**Status:** Accepted  
**Date:** 2026-06-24  

## Context

The research agent needs to execute a multi-step pipeline: plan → search → extract → synthesize → verify → (possibly loop back). Early options considered:

- **Plain Python** with `asyncio` — full control but no workflow primitives; we'd build state management, retries, and branching from scratch.
- **LangChain** — mature agent/tool framework but linear chain-of-thought doesn't naturally support conditional loops (verify → re-search).
- **CrewAI / AutoGen** — multi-agent frameworks; overengineered for a single research agent.

The pipeline has non-linear control flow: the Verify node may need to loop back to Search for re-research, which demands a graph-based execution model.

## Decision

Use **LangGraph** as the orchestration framework.

LangGraph models the pipeline as a state machine with typed state passing between nodes. Conditional edges (e.g., "if verification reveals gaps, route back to Search; else route to Output") map directly to LangGraph's `add_conditional_edges`.

## Consequences

### Positive
- Graph structure matches the non-linear pipeline naturally.
- Built-in streaming (`graph.stream()`) feeds our SSE progress events to the frontend.
- State is a typed `TypedDict` — easy to persist incrementally to PostgreSQL.
- LangGraph has first-class LangChain integration (for Tavily, chat models) but doesn't require it.

### Negative
- Adds a framework dependency that could be avoided with a simple `while` loop in plain Python.
- Debugging LangGraph state transitions is harder than a linear script.
- Team must learn LangGraph idioms (nodes, edges, state modifiers, checkpointing).

### Trade-offs considered
- Plain Python would be simpler but would require building loop + state machinery ourselves.
- LangChain `SequentialChain` doesn't support conditional re-search loops.
