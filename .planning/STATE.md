# Project State: Am I Better Than Yesterday?

**Last Updated:** 2026-01-21

## Project Reference

**Core Value:** Consistency and momentum toward personal goals - determining if today maintained or exceeded yesterday.

**Current Focus:** AI Evaluation Pipeline - building the backend that analyzes daily journals and delivers verdicts.

## Current Position

**Milestone:** AI Evaluation Pipeline
**Phase:** 2 of 7 (Scoring Foundation)
**Plan:** 1 of 3 complete
**Status:** In progress
**Last Activity:** 2026-01-21 - Completed 02-01-PLAN.md

**Progress:**
```
Phases:    [##-----] 2/7 (Phase 1 complete, Phase 2 in progress)
Plans:     [##--------------] 2/17 total
Tasks:     [########] 3/3 (plan 02-01)
```

## Phase Overview

| Phase | Name | Status |
|-------|------|--------|
| 1 | Voice Transcription | Complete |
| 2 | Scoring Foundation | In Progress (1/3 plans) |
| 3 | Signal Extraction | Pending |
| 4 | Historical Trends | Pending |
| 5 | Verdict Generation | Pending |
| 6 | Evening Orchestration | Pending |
| 7 | Smart Notifications | Pending |

## Performance Metrics

| Metric | Value |
|--------|-------|
| Plans completed | 2 |
| Tasks completed | 6 |
| Blockers encountered | 0 |
| Research pivots | 0 |

## Accumulated Context

### Key Decisions

| Decision | Rationale | Date |
|----------|-----------|------|
| Deterministic-first scoring | Pure LLM scoring shows ~40% inconsistency; hybrid approach provides explainability | 2026-01-19 |
| Voice as Phase 1 | Independent capability, can proceed in parallel with planning Phase 2 | 2026-01-19 |
| Mood classification before verdicts | Delivering criticism to struggling user is trust-destroying; research flagged as critical | 2026-01-19 |
| Validate audio content type at endpoint | Fail fast before hitting OpenAI API; clearer error messages | 2026-01-19 |
| TranscriptionService stateless | Transcription is pure operation; journal persistence handled separately | 2026-01-19 |
| Keyword-based categories extensible | Pre-defined keywords for common goals, fallback to category name | 2026-01-21 |
| Scoring formula: 30+20+30+10+10 | Base points (showed up) + keywords + effort + quantifiers + evidence = 100 max | 2026-01-21 |
| Evidence limited to top 3 sentences | Keeps reasoning concise while preserving proof | 2026-01-21 |

### Open TODOs

- Set OPENAI_API_KEY environment variable before using voice transcription

### Blockers

- None

### Research Flags

From research/SUMMARY.md:
- Phase 4 (Historical/RAG): Embedding drift mitigation strategies need deeper investigation
- Phase 5 (Verdicts): Emotional AI safety patterns and crisis detection warrant careful specification

## Session Continuity

**Last Session:** 2026-01-21 - Completed Phase 2 Plan 1 (Deterministic Scoring Foundation)
**Stopped At:** Completed 02-01-PLAN.md
**Resume File:** None

**Next Action:** Continue Phase 2 with Plan 02 (LLM Enhancement) or Plan 03 (Integration)

**Context to Preserve:**
- Voice transcription endpoint complete: POST /api/v1/voice/transcribe
- JournalService has append_content method for voice accumulation
- TranscriptionService uses OpenAI Whisper API (requires OPENAI_API_KEY)
- **DeterministicScorer class complete:** score_goal and score_entry methods
- **Scoring schemas:** GoalScoreInput, GoalScoreOutput, ScoringResult with Pydantic validation
- **Deterministic scoring verified:** Same input produces identical output
- **Evidence extraction:** Captures relevant journal sentences as proof
- Existing codebase has FastAPI backend, auth, journals, goals, database models
- Celery + Redis configured but not implemented
- Research recommends instructor for structured outputs
- pgvector 0.8+ already configured for embeddings

---

*State updated: 2026-01-21*
