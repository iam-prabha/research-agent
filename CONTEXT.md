# Research Agent — Domain Glossary

## Core Entities

### ResearchSession
A single end-to-end invocation of the agent, from user query to final report. Writes each stage incrementally to PostgreSQL. Lifecycle states: `planning → searching → extracting → synthesizing → verifying → completed | failed`.

### ResearchQuery
The raw topic string the user submits (e.g. "history of quantum computing").

### SubQuestion
A decomposed research question produced by the Plan node. Every SubQuestion is a child of exactly one ResearchSession. Each SubQuestion drives one or more Tavily searches and becomes a section in the final report.

### SourceDocument
A web page returned by the search provider. Belongs to one ResearchSession and optionally to one SubQuestion. Carries a URL, title, API snippet, and full extracted text.

### ExtractedClaim
An atomic factual statement extracted from a SourceDocument by the Extract node. Examples: *"Quantum entanglement was first described in 1935"*, *"EPR paradox challenged locality"*. Always linked to exactly one SourceDocument.

### VerificationCheck
The outcome of checking one ExtractedClaim against its SourceDocument's full text. Carries a status: `confirmed`, `contradicted`, `unverifiable`. A single claim may have multiple VerificationChecks across re-search loops.

### ResearchReport
The final Markdown output. Contains section-per-SubQuestion and a Bibliography appendix. Footnotes `[N]` inline reference numbered Bibliography entries.

### BibliographyEntry
One cited source in the report appendix. Format: `[N] Title — URL (accessed YYYY-MM-DD)`.

## Relationships

```
ResearchSession 1──* SubQuestion
ResearchSession 1──* SourceDocument
ResearchSession 1──* ExtractedClaim
ResearchSession 1──1 ResearchReport
SubQuestion 1──* SourceDocument
SourceDocument 1──* ExtractedClaim
ExtractedClaim 1──* VerificationCheck
ResearchReport *──* BibliographyEntry  (embedded in Markdown)
ResearchReport *──* Footnote            (embedded in Markdown)
```

## Key Invariants

- Every ExtractedClaim must reference at least one SourceDocument.
- Every Footnote `[N]` in the report must have a matching BibliographyEntry.
- Unverifiable claims are surfaced transparently in the report, never dropped silently.
- At most 3 search rounds per SubQuestion (initial + 2 re-searches).
