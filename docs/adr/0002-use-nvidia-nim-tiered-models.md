# ADR 0002: Use NVIDIA NIM with tiered model allocation

**Status:** Accepted  
**Date:** 2026-06-24  

## Context

The agent needs LLM inference for four distinct tasks with different quality/cost requirements:

| Node | Complexity | Volume |
|------|-----------|--------|
| Plan | Query decomposition | 1 call per session |
| Extract | Summarize sources, extract claims | N calls per session (one per source) |
| Synthesize | Write report with structured citations | 1 call per session |
| Verify | Cross-check claims against source text | 1 call per session |

Frontier model APIs (Claude, GPT-4o) would work for all four but cost more for high-volume Extract calls. A single free-tier endpoint (NIM) risks quality issues on the critical Synthesize and Verify nodes.

## Decision

Use **NVIDIA NIM (build.nvidia.com free tier)** with tiered model allocation:

| Node | Model | Rationale |
|------|-------|-----------|
| Plan | Llama 3.1 8B Instruct | Fast, cheap, adequate for decomposition |
| Extract | Llama 3.1 8B Instruct | Batch-friendly, many calls, doesn't need frontier quality |
| Synthesize | Llama 3.1 70B Instruct | Report quality critical; larger model for structured output |
| Verify | Llama 3.1 70B Instruct | Factual precision critical; needs strong reasoning |

All models accessed via NIM's OpenAI-compatible API endpoint.

## Consequences

### Positive
- Cost-effective: cheap models for high-volume nodes, quality models for critical nodes.
- All models behind a single API endpoint — no multi-provider auth complexity.
- NIM free tier has no rate limit on the public endpoint (subject to NVIDIA's terms).

### Negative
- Open-weight models (Llama 3.1) are weaker at strict structured output than frontier models (Claude, GPT-4o). Synthesize prompts must be engineered carefully.
- NIM free tier availability is not guaranteed long-term.
- Tiered model config adds complexity vs. using one model everywhere.

### Trade-offs considered
- Single model (70B everywhere): simpler but 4x the cost per Extract call.
- Claude/GPT: higher quality but paid API, not free tier, and requires a second provider key.
