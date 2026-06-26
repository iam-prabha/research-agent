# ADR 0003: PostgreSQL with incremental per-node persistence

**Status:** Accepted  
**Date:** 2026-06-24  

## Context

The agent needs to store research session data. Options considered:

- **No database** — ephemeral in-memory only; loses all data on restart, no audit trail.
- **SQLite** — simple, no server needed, but concurrent access is limited and Neon/cloud PG not supported.
- **PostgreSQL via SQLAlchemy** — production-grade, connection-string swappable (local PG, Neon, RDS), Alembic for migrations.

The decision to persist the *full* research session (not just the final report) was driven by the quality goal: we need to trace which sources fed which claims, and which verification checks passed/failed, to audit any report.

## Decision

Use **PostgreSQL** accessed through **SQLAlchemy** with **Alembic** migrations. Each LangGraph node writes its results to the DB incrementally:

1. Session starts → `ResearchSession` row created with `status=planning`
2. Plan node → `SubQuestion` rows inserted
3. Search node → `SourceDocument` rows inserted
4. Extract node → `ExtractedClaim` rows inserted, linked to sources
5. Synthesize node → `ResearchSession.report_markdown` updated
6. Verify node → `VerificationCheck` rows inserted
7. Session completes → `ResearchSession.status = completed`

Connection string from `.env` (`DATABASE_URL`), supporting any PostgreSQL-compatible platform (Neon, RDS, Supabase, local).

## Consequences

### Positive
- Full audit trail: every claim is traceable to its source and verification outcome.
- Incremental writes mean partial progress survives crashes.
- Enables future features: session history, re-verify old reports, compare across sessions.

### Negative
- Database dependency adds operational complexity (migrations, connection pooling, SSL).
- Each node now has a side effect (DB write) in addition to its LLM call, making individual node testing harder.
- Schema changes require Alembic migrations.

### Trade-offs considered
- SQLite: simpler for dev, but would break the connection-string-swappable goal (Neon etc.).
- End-only persistence: simpler but loses partial progress on crash.
