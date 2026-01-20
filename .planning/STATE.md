# Project State: Am I Better Than Yesterday?

**Last Updated:** 2026-01-21

## Project Reference

**Core Value:** Consistency and momentum toward personal goals - determining if today maintained or exceeded yesterday.

**Current Focus:** AI Evaluation Pipeline - building the backend that analyzes daily journals and delivers verdicts.

## Current Position

**Milestone:** AI Evaluation Pipeline
**Phase:** 2 of 7 (Scoring Foundation)
**Plan:** 2 of 3 complete
**Status:** In progress
**Last Activity:** 2026-01-21 - Completed 02-02-PLAN.md

**Progress:**
```
Phases:    [##-----] 2/7 (Phase 1 complete, Phase 2 in progress)
Plans:     [###-------------] 3/17 total
Tasks:     [########] 3/3 (plan 02-02)
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
| Plans completed | 3 |
| Tasks completed | 9 |
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
| Use instructor for structured LLM outputs | Provides automatic Pydantic parsing and retry logic, eliminating manual JSON parsing | 2026-01-21 |
| Double-enforce +/-20% guardrails | Field validator + post-response clamping ensures adjustment limit never exceeded | 2026-01-21 |
| Mock classes for testing | MockLLMScoreEnhancer mirrors real API, enables testing without API calls or costs | 2026-01-21 |
| Claude Sonnet 4 for contextual analysis | Model specified in research as optimal for text analysis and emotional nuance | 2026-01-21 |

### Open TODOs

- Set OPENAI_API_KEY environment variable before using voice transcription
- Set ANTHROPIC_API_KEY environment variable before using LLM score enhancement

### Blockers

- None

### Research Flags

From research/SUMMARY.md:
- Phase 4 (Historical/RAG): Embedding drift mitigation strategies need deeper investigation
- Phase 5 (Verdicts): Emotional AI safety patterns and crisis detection warrant careful specification

## Session Continuity

**Last Session:** 2026-01-21 - Completed Phase 2 Plan 2 (LLM Score Enhancement)
**Stopped At:** Completed 02-02-PLAN.md
**Resume File:** None

**Next Action:** Continue Phase 2 with Plan 03 (Integration) - wire deterministic + LLM enhancement together

**Context to Preserve:**
- Voice transcription endpoint complete: POST /api/v1/voice/transcribe
- JournalService has append_content method for voice accumulation
- TranscriptionService uses OpenAI Whisper API (requires OPENAI_API_KEY)
- **DeterministicScorer class complete:** score_goal and score_entry methods
- **Scoring schemas:** GoalScoreInput, GoalScoreOutput, ScoringResult with Pydantic validation
- **Deterministic scoring verified:** Same input produces identical output
- **Evidence extraction:** Captures relevant journal sentences as proof
- **LLMScoreEnhancer class complete:** enhance_score and enhance_scoring_result methods
- **EnhancedScore model:** +/-20% guardrails enforced via validator + clamping
- **MockLLMScoreEnhancer:** Testing without API calls
- **Prompt templates:** SCORE_ENHANCEMENT_PROMPT with contextual guidance
- **instructor integration:** Structured outputs from Claude using Pydantic
- Existing codebase has FastAPI backend, auth, journals, goals, database models
- Celery + Redis configured but not implemented
- pgvector 0.8+ already configured for embeddings

---

*State updated: 2026-01-21*
