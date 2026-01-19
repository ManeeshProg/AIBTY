# Am I Better Than Yesterday?

## What This Is

An AI-driven personal growth application that helps users objectively track self-improvement through daily journaling. Users log activities throughout the day (text or voice), and each evening the AI analyzes their entries, compares with their historical trajectory, and delivers a verdict: better, same, or worse than yesterday — with emotional messaging, goal breakdowns, and actionable guidance for tomorrow.

## Core Value

**Consistency and momentum toward personal goals.** The AI must accurately determine if today's effort maintained or exceeded yesterday's, and communicate that in a way that drives continued action — celebrating wins and poking egos when users slip.

## Requirements

### Validated

<!-- Existing capabilities from codebase -->

- ✓ User authentication (signup, login, JWT sessions) — existing
- ✓ Password hashing with bcrypt — existing
- ✓ Journal entry CRUD (create, read, update, delete) — existing
- ✓ Goals CRUD (create, read, update, delete) — existing
- ✓ Database models for DailyScore, ScoreMetric, ExtractedMetric — existing (scaffolded)
- ✓ pgvector extension for embeddings — existing (configured)
- ✓ Async SQLAlchemy 2.0 patterns — existing
- ✓ Alembic migrations — existing

### Active

<!-- Backend AI Pipeline - This Milestone -->

- [ ] Voice transcription via Whisper API
- [ ] Multiple journal entries per day (accumulate throughout day)
- [ ] Signal extraction from entries (productivity, fitness, learning, discipline, well-being)
- [ ] Activity-to-goal mapping (connect extracted activities to user's stated goals)
- [ ] Full RAG system with pgvector (embed entries, retrieve historical context)
- [ ] Deterministic scoring rules combined with LLM reasoning
- [ ] Verdict generation (better/same/worse) with:
  - [ ] Emotional messaging (encouraging when better, ego-poking when worse)
  - [ ] Score breakdown per goal
  - [ ] Overall score and streak tracking
  - [ ] Actionable push for tomorrow
- [ ] Scheduled evening analysis (Celery task at user's configured time)
- [ ] Smart notification triggers (detect who hasn't logged, generate provocative nudge)
- [ ] Historical trend data for visualization (consumed by mobile later)

### Out of Scope

- Mobile app UI — deferred to next milestone
- On-device RAG/offline AI — deferred, requires mobile-specific architecture
- Real-time collaboration — single-user app
- Social features — personal growth is private
- OAuth/social login — email/password sufficient for v1
- Audio file storage — transcribe immediately, don't persist audio

## Context

**Existing Codebase:**
- FastAPI backend with layered architecture (API → Services → Models)
- PostgreSQL with pgvector for embeddings
- Celery + Redis configured but not yet implemented
- AI pipeline directories scaffolded but empty (`backend/app/ai_pipeline/`)
- Mobile app directory exists but no source files

**AI Stack:**
- Claude (Anthropic) as primary LLM for analysis and coaching
- OpenAI for embeddings (text-embedding-3-small) and Whisper transcription
- LangChain installed for orchestration

**User Philosophy:**
- "Better" means consistency and momentum — not underperforming vs yesterday
- Rest days are acknowledged but not celebrated — "the world doesn't stop"
- Every day counts, no free passes
- Showing up matters, but intensity/difficulty elevates
- The AI voice is supportive but has edge — celebrates wins, pokes egos on slips

**Example Messaging Tone:**
- Better day: "You showed up harder than yesterday. This is how you become someone different."
- Worse day: "Remember those goals? They didn't take a day off. What happened?"
- No entries: "Nothing worth mentioning today?" / "Yesterday you did 3 hard problems. Today... silence?"

## Constraints

- **LLM Provider**: Claude for analysis/coaching, OpenAI for embeddings/transcription — per existing dependencies
- **Database**: PostgreSQL with pgvector — already configured
- **Task Queue**: Celery with Redis — already in requirements
- **Backend Only**: This milestone focuses on API and AI pipeline, no mobile UI
- **Privacy**: Journal content is sensitive — no third-party analytics, minimal logging of content

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Full RAG over week-only context | Long-term trajectory is core value prop — "best coding week since October" | — Pending |
| Backend-triggered notifications | Backend knows who hasn't logged, can craft smart messages | — Pending |
| Scheduled evening analysis | Consistent ritual, no user action required | — Pending |
| Deterministic + LLM scoring | Consistency and explainability without losing nuance | — Pending |
| Voice AND text input | User chooses their preferred logging method | — Pending |

---
*Last updated: 2026-01-19 after initialization*
