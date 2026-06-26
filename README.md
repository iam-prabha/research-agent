# Research Agent

AI-powered research agent with citation-grounded factual reporting. Decomposes a topic into sub-questions, searches the web, extracts claims, synthesizes a Markdown report with inline footnotes, and verifies claims against source documents.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI, LangGraph, SQLAlchemy, PostgreSQL |
| LLM | NVIDIA NIM (build.nvidia.com) — Llama 3.1 8B/70B |
| Search | Tavily API |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS v4 |
| Runtime | `uv` (package manager), Docker |

## Quick Start

**Prerequisites:** Python 3.12+, `uv`, Node.js 20+, PostgreSQL

```bash
# 1. Backend
cd backend
cp .env.example .env        # fill in your API keys and DATABASE_URL
uv sync
uv run uvicorn app.main:app --reload

# 2. Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in a browser.

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `NVIDIA_API_KEY` | Yes | — | NVIDIA NIM API key |
| `TAVILY_API_KEY` | Yes | — | Tavily search API key |
| `DATABASE_URL` | Yes | — | PostgreSQL connection string |
| `MAX_SEARCH_ROUNDS` | No | `3` | Max search rounds per topic |
| `PLAN_MODEL` | No | `meta/llama-3.1-8b-instruct` | Model for planning |
| `EXTRACT_MODEL` | No | `meta/llama-3.1-8b-instruct` | Model for extraction |
| `SYNTHESIZE_MODEL` | No | `meta/llama-3.1-70b-instruct` | Model for report writing |
| `VERIFY_MODEL` | No | `meta/llama-3.1-70b-instruct` | Model for fact-checking |

## API

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/research` | Start a new research session |
| `GET` | `/api/research/history` | List recent sessions (max 20) |
| `GET` | `/api/research/{id}` | Get session details and report |
| `GET` | `/api/research/{id}/stream` | SSE stream for live progress |
| `DELETE` | `/api/research/{id}` | Delete a session and all its data |

## Docker

```bash
docker compose up --build
```

## Architecture

```
User query → Plan → Search → Extract → Synthesize → Verify → Report
                ↑                                    |
                └────── re-search loop ──────────────┘
```

- **Plan** — decomposes the topic into 3–6 self-contained sub-questions
- **Search** — queries Tavily for each sub-question, stores source documents
- **Extract** — LLM extracts atomic factual claims from each source
- **Synthesize** — LLM writes a Markdown report with `[N]` inline footnotes and a bibliography
- **Verify** — LLM fact-checks each claim against its source document. Unverified claims trigger a re-search cycle (up to `MAX_SEARCH_ROUNDS`)

Each stage writes incrementally to PostgreSQL. SSE streaming pushes real-time status events to the React frontend.

## Project Structure

```
backend/
  app/
    main.py          — FastAPI server, routes, SSE streaming
    graph.py         — LangGraph state graph definition
    state.py         — GraphState type
    config.py        — Pydantic settings from env
    models.py        — SQLAlchemy ORM models
    db.py            — Database engine and session
    nodes/
      plan.py        — Topic → sub-questions
      search.py      — Sub-questions → source documents
      extract.py     — Sources → extracted claims
      synthesize.py  — Sources + claims → Markdown report
      verify.py      — Claims → verification results
frontend/
  src/
    pages/
      HomePage.tsx       — Landing page with search form + stepper
      ReportPage.tsx     — Report view with Markdown rendering
    components/
      SearchForm.tsx     — Query input form
      ProgressStepper.tsx — Live step indicator
      HistorySidebar.tsx — Session history drawer
      AppLayout.tsx      — Shared layout wrapper
      Toolbar.tsx        — Copy / download buttons
    context/
      ResearchContext.tsx — State management via useReducer
    api/
      sse.ts             — EventSource SSE client
```
