# Project State: Am I Better Than Yesterday?

**Last Updated:** 2026-01-21

## Project Reference

**Core Value:** Consistency and momentum toward personal goals - determining if today maintained or exceeded yesterday.

**Current Focus:** AI Evaluation Pipeline - building the backend that analyzes daily journals and delivers verdicts.

## Current Position

**Milestone:** AI Evaluation Pipeline
**Phase:** 3 of 7 (Signal Extraction)
**Plan:** 1 of 1 complete
**Status:** Phase complete
**Last Activity:** 2026-01-21 - Completed 03-01-PLAN.md

**Progress:**
```
Phases:    [###----] 3/7 (Phase 3 complete)
Plans:     [#####-----------] 5/17 total
Tasks:     [###] 3/3 (plan 03-01)
```

## Phase Overview

| Phase | Name | Status |
|-------|------|--------|
| 1 | Voice Transcription | Complete |
| 2 | Scoring Foundation | Complete |
| 3 | Signal Extraction | Complete |
| 4 | Historical Trends | Pending |
| 5 | Verdict Generation | Pending |
| 6 | Evening Orchestration | Pending |
| 7 | Smart Notifications | Pending |

## Performance Metrics

| Metric | Value |
|--------|-------|
| Plans completed | 5 |
| Tasks completed | 15 |
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
| SAME_THRESHOLD = 5.0 | Within 5 points = "same" verdict; prevents false positives on minor fluctuations | 2026-01-21 |
| Upsert strategy for DailyScore | Allows re-scoring same date (idempotent); deletes old metrics and creates fresh | 2026-01-21 |
| Streak continues with threshold | Streak continues when score ≥ (previous - SAME_THRESHOLD); separate per goal | 2026-01-21 |
| Composite score weighting | Weighted average: sum(score × weight) / sum(weights); honors UserGoal.weight | 2026-01-21 |
| Temperature 0.2 for extraction | Lower temperature for consistent structured extraction from journal text | 2026-01-21 |
| Seven standard activity categories | productivity, fitness, learning, discipline, well-being, creativity, social - aligns with common goal types | 2026-01-21 |
| Confidence scoring for extractions | 1.0 for explicit numbers, 0.7-0.9 for inferred values - enables quality filtering | 2026-01-21 |

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

**Last Session:** 2026-01-21 - Completed Phase 3 Plan 1 (Signal Extraction)
**Stopped At:** Completed 03-01-PLAN.md - Phase 3 complete
**Resume File:** None

**Next Action:** Begin Phase 4 (Historical Trends) - RAG and trend analysis

**Context to Preserve:**
- **Phase 1 (Voice) complete:** POST /api/v1/voice/transcribe for voice journaling
- **Phase 2 (Scoring) complete:** Full scoring pipeline operational
- **Phase 3 (Extraction) complete:** ExtractionAgent + ExtractionService operational
- **ScoringService orchestrates:** deterministic → LLM → comparison → streaks → persistence
- **Scoring endpoints:** POST /scores/score, GET /scores/today, GET /scores/{date}, GET /streaks/all, GET /history
- **DeterministicScorer:** Keyword matching, effort detection, base scoring (0-100)
- **LLMScoreEnhancer:** Contextual adjustment within +/-20% guardrails using Claude Sonnet 4
- **ExtractionAgent:** Claude Sonnet 4 + instructor for structured activity extraction
- **ExtractionService:** extract_and_persist(), get_metrics_for_entry(), clear_metrics_for_entry()
- **ExtractedMetric table:** Populated with category, key, value, evidence, confidence from journal entries
- **MockLLMScoreEnhancer:** Testing fallback when ANTHROPIC_API_KEY not set
- **Verdict system:** better/same/worse/first_day with 5.0 point SAME_THRESHOLD
- **Streak tracking:** current_streak and longest_streak per goal category
- **Persistence:** DailyScore and ScoreMetric tables with upsert support
- **Seven activity categories:** productivity, fitness, learning, discipline, well-being, creativity, social
- **instructor library:** ^1.14.0 for structured LLM outputs with Pydantic
- Existing codebase has FastAPI backend, auth, journals, goals, database models
- Celery + Redis configured but not implemented
- pgvector 0.8+ already configured for embeddings

---

*State updated: 2026-01-21*
