# Project State: Am I Better Than Yesterday?

**Last Updated:** 2026-01-25T13:45:00Z

## Project Reference

**Core Value:** Consistency and momentum toward personal goals - determining if today maintained or exceeded yesterday.

**Current Focus:** AI Evaluation Pipeline - building the backend that analyzes daily journals and delivers verdicts.

## Current Position

**Milestone:** AI Evaluation Pipeline
**Phase:** 7 of 7 (Smart Notifications) - In Progress
**Plan:** 3 of 4 complete
**Status:** In progress
**Last Activity:** 2026-01-25 - Completed 07-02-PLAN.md (NotificationService)

**Progress:**
```
Phases:    [######.] 7/7 (Phase 7 in progress)
Plans:     [################-] 17/18 total
Tasks:     [######--] 7/8 (phase 7)
```

## Phase Overview

| Phase | Name | Status |
|-------|------|--------|
| 1 | Voice Transcription | Complete |
| 2 | Scoring Foundation | Complete |
| 3 | Signal Extraction | Complete |
| 4 | Historical Trends | Complete |
| 5 | Verdict Generation | Complete |
| 6 | Evening Orchestration | Complete |
| 7 | Smart Notifications | In Progress |

## Performance Metrics

| Metric | Value |
|--------|-------|
| Plans completed | 17 |
| Tasks completed | 49 |
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
| Streak continues with threshold | Streak continues when score >= (previous - SAME_THRESHOLD); separate per goal | 2026-01-21 |
| Composite score weighting | Weighted average: sum(score * weight) / sum(weights); honors UserGoal.weight | 2026-01-21 |
| Temperature 0.2 for extraction | Lower temperature for consistent structured extraction from journal text | 2026-01-21 |
| Seven standard activity categories | productivity, fitness, learning, discipline, well-being, creativity, social - aligns with common goal types | 2026-01-21 |
| Confidence scoring for extractions | 1.0 for explicit numbers, 0.7-0.9 for inferred values - enables quality filtering | 2026-01-21 |
| Category exact match scores 1.0, fuzzy 0.7 | Primary matching on category exact match, secondary on keyword fuzzy match for goal mapping | 2026-01-21 |
| Fuzzy matching uses significant words | Words >3 chars from metric key checked against goal description - avoids false positives | 2026-01-21 |
| Goal suggestions require frequency >= 3 | Balances between catching patterns and avoiding noise from one-off mentions | 2026-01-21 |
| Category-specific description templates | Different goal types need different framing (track vs maintain vs build) | 2026-01-21 |
| Extraction runs on all journal save operations | Ensures extracted metrics always reflect current journal content | 2026-01-21 |
| Clear metrics before re-extraction | Idempotent extraction - editing journals doesn't create duplicates | 2026-01-21 |
| PUT routes through create_or_update | Single code path ensures extraction consistency | 2026-01-21 |
| Sparse trend data (no gap filling) | Frontend handles missing days; keeps API simple and flexible | 2026-01-25 |
| Pre-computed trend direction | Mobile doesn't calculate; API returns "improving"/"declining"/"stable"/"insufficient_data" | 2026-01-25 |
| 5% threshold for trend changes | Matches SAME_THRESHOLD logic; prevents noise in week-over-week comparisons | 2026-01-25 |
| Week = 7 days, not calendar week | Consistent window regardless of query day | 2026-01-25 |
| Three-tier mood classification | struggling/stable/thriving - simple classification reduces error risk | 2026-01-25 |
| Crisis flag always supportive_only | Never deliver edge messaging to someone in crisis | 2026-01-25 |
| min_length=1 for activity_references | Prevents generic "Great job!" messages | 2026-01-25 |
| min_length=1 for tomorrow_actions | Ensures actionable guidance is always provided | 2026-01-25 |
| Three tone tiers for verdicts | supportive_only/light_edge/full_edge maps to mood classification | 2026-01-25 |
| Mock fallback without API key | Development without API costs using MockMoodClassifier/MockVerdictGenerator | 2026-01-25 |
| Default analysis_time 21:00 UTC | Evening time when daily activities complete; explicit timezone config required | 2026-01-25 |
| celeryconfig.py in backend root | Celery config_from_object loads from Python path; backend root is on path | 2026-01-25 |
| Unique constraint user_date | One analysis per user per day for idempotency | 2026-01-25 |
| Retry strategy exponential backoff | Max 3 retries with 1 hour max delay and jitter | 2026-01-25 |
| zoneinfo for timezone handling | Per-user timezone conversion using Python stdlib | 2026-01-25 |
| Failed analysis retry allowed | Failed analyses can be retried; completed ones are skipped | 2026-01-25 |
| Ownership verification on notifications | Check user_id match before modifying notifications for security | 2026-01-25 |
| Mobile polling for notifications | GET /notifications returns pending only; mobile polls then delivers locally | 2026-01-25 |
| Python filtering over SQL for JSON preferences | Simpler query that works across SQLite/PostgreSQL for non-logger detection | 2026-01-25 |
| Default notification time 18:00 | Evening default when users likely done with daily activities | 2026-01-25 |
| Ego-poking tone tiers | Messages escalate based on inactivity: 1 day, 2-3 days, 4-7 days, 7+ days | 2026-01-25 |
| Activity summary lookback 7 days | Balance between recent context and meaningful patterns | 2026-01-25 |

### Open TODOs

- Set OPENAI_API_KEY environment variable before using voice transcription
- Set ANTHROPIC_API_KEY environment variable before using LLM score enhancement and extraction
- Full pipeline integration in AnalysisOrchestrator.run_analysis() (connects extraction, scoring, verdicts)

### Blockers

- None

### Research Flags

From research/SUMMARY.md:
- Phase 4 (Historical/RAG): Embedding drift mitigation strategies need deeper investigation
- Phase 5 (Verdicts): Emotional AI safety patterns and crisis detection warrant careful specification

## Session Continuity

**Last Session:** 2026-01-25 - Completed NotificationService (07-02)
**Stopped At:** Plan 07-02 complete - Ready for 07-04 (Notification Scheduling)
**Resume File:** None

**Next Action:** Execute Phase 7 Plan 04 (Notification Scheduling)

**Context to Preserve:**
- **Phase 1 (Voice) complete:** POST /api/v1/voice/transcribe for voice journaling
- **Phase 2 (Scoring) complete:** Full scoring pipeline operational
- **Phase 3 (Extraction) complete:** Full extraction pipeline operational and integrated
- **Phase 4 (Trends) complete:** Historical trend analysis operational
- **Phase 5 (Verdicts) complete:** Mood-aware verdict generation operational
- **Phase 6 (Orchestration) complete:** Evening analysis scheduling operational
- **ScoringService orchestrates:** deterministic -> LLM -> comparison -> streaks -> persistence
- **Scoring endpoints:** POST /scores/score, GET /scores/today, GET /scores/{date}, GET /streaks/all, GET /history
- **Trends endpoints:** GET /trends/, GET /trends/{goal_category}
- **TrendService:** get_goal_trend(), get_all_goals_trends(), calculate_week_over_week()
- **Trend schemas:** TrendDataPoint, WeekOverWeekComparison, GoalTrendRead, TrendsResponse
- **DeterministicScorer:** Keyword matching, effort detection, base scoring (0-100)
- **LLMScoreEnhancer:** Contextual adjustment within +/-20% guardrails using Claude Sonnet 4
- **ExtractionAgent:** Claude Sonnet 4 + instructor for structured activity extraction
- **ExtractionService:** extract_and_persist(), get_metrics_for_entry(), clear_metrics_for_entry(), map_metrics_to_goals(), suggest_goals()
- **ExtractedMetric table:** Populated with category, key, value, evidence, confidence from journal entries
- **GoalActivityLink table:** Links ExtractedMetric to UserGoal with match_reason and contribution_score
- **Goal mapping:** Category exact match (1.0) + keyword fuzzy match (0.7)
- **Goal suggestions:** Pattern-based suggestions for unmatched recurring activities (frequency >= 3)
- **GET /api/v1/goals/suggestions:** Exposes goal suggestions with configurable lookback (7-90 days)
- **Journal save triggers extraction:** create_or_update() and append_content() both call extraction pipeline
- **MockLLMScoreEnhancer:** Testing fallback when ANTHROPIC_API_KEY not set
- **Verdict system:** better/same/worse/first_day with 5.0 point SAME_THRESHOLD
- **MoodClassifier:** Classifies journal content as struggling/stable/thriving with crisis detection
- **VerdictGenerator:** Creates emotional verdicts with activity-specific messaging and tomorrow actions
- **VerdictService:** Orchestrates mood classification + verdict generation
- **Verdicts endpoints:** POST /verdicts/generate, GET /verdicts/today
- **User preferences endpoints:** GET/PATCH /api/v1/users/me/preferences (analysis_time, timezone)
- **Three tone tiers:** supportive_only (struggling), light_edge (stable), full_edge (thriving)
- **Streak tracking:** current_streak and longest_streak per goal category
- **Persistence:** DailyScore and ScoreMetric tables with upsert support
- **Seven activity categories:** productivity, fitness, learning, discipline, well-being, creativity, social
- **instructor library:** ^1.14.0 for structured LLM outputs with Pydantic
- Existing codebase has FastAPI backend, auth, journals, goals, database models
- **Celery app configured:** celery_app.py with Redis broker, celeryconfig.py with beat schedule
- **Beat schedule:** check_due_analyses task runs every minute
- **Task routing:** orchestrator tasks to default queue, analysis tasks to analysis queue
- **Tasks package:** app.tasks with orchestrator module
- **AnalysisRun model:** Tracks analysis executions with status, retries, timing
- **AnalysisOrchestrator:** Coordinates evening analysis pipeline
- **Celery tasks:** check_due_analyses (periodic), run_user_analysis (with retries), run_manual_analysis (API trigger)
- pgvector 0.8+ already configured for embeddings
- **Notification model:** Stores pending notifications with delivery tracking
- **Notification types:** reminder, verdict, system
- **NotificationRead, NotificationPreferencesUpdate schemas:** Ready for API
- **Notification API endpoints:** GET /notifications, GET/PATCH /notifications/preferences, PATCH /{id}/delivered, PATCH /{id}/read, PATCH /{id}/dismiss
- **NotificationService (full):** get_non_loggers(), get_user_activity_summary(), generate_reminder_message(), create_notification(), get_pending_notifications(), mark_delivered(), mark_read(), dismiss_notification()

---

*State updated: 2026-01-25T13:45:00Z*
