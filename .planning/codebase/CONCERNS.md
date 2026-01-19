# Codebase Concerns

**Analysis Date:** 2026-01-19

## Tech Debt

**Mobile Application Not Implemented:**
- Issue: The `mobile/` directory contains empty scaffolded folders with no actual code
- Files: `D:/projects/AI/amibetter/mobile/app/`, `D:/projects/AI/amibetter/mobile/components/`, `D:/projects/AI/amibetter/mobile/hooks/`, `D:/projects/AI/amibetter/mobile/lib/`, `D:/projects/AI/amibetter/mobile/providers/`, `D:/projects/AI/amibetter/mobile/types/`
- Impact: No client application exists; backend cannot be tested end-to-end with a real UI
- Fix approach: Implement React Native/Expo mobile app per IMPLEMENTATION_PLAN.md Phase 4-5 specifications

**AI Pipeline Not Implemented:**
- Issue: The `backend/app/ai_pipeline/` directory structure exists but contains no code
- Files: `D:/projects/AI/amibetter/backend/app/ai_pipeline/agents/`, `D:/projects/AI/amibetter/backend/app/ai_pipeline/prompts/`, `D:/projects/AI/amibetter/backend/app/ai_pipeline/rag/`
- Impact: Core differentiating feature (AI scoring, metric extraction, coaching) is completely missing; application cannot deliver its core value proposition
- Fix approach: Implement orchestrator, extraction agent, scoring engine, RAG retriever, and coach agent per IMPLEMENTATION_PLAN.md Phase 2-3

**Missing Score/Insights API Endpoints:**
- Issue: `/api/v1/scores` and `/api/v1/insights` endpoints specified in IMPLEMENTATION_PLAN.md do not exist
- Files: `D:/projects/AI/amibetter/backend/app/api/v1/router.py` (only includes auth, journals, goals)
- Impact: No way to trigger AI evaluation or retrieve daily scores
- Fix approach: Create `D:/projects/AI/amibetter/backend/app/api/v1/scores.py` with evaluate, status, history, and trends endpoints

**No Score Service:**
- Issue: ScoreService for DailyScore CRUD operations does not exist
- Files: Missing `D:/projects/AI/amibetter/backend/app/services/score_service.py`
- Impact: DailyScore and ScoreMetric models exist but have no service layer
- Fix approach: Create ScoreService following existing service patterns in `D:/projects/AI/amibetter/backend/app/services/`

**Dependency Duplication:**
- Issue: Both `pyproject.toml` (Poetry) and `requirements.txt` exist with different version specs
- Files: `D:/projects/AI/amibetter/backend/pyproject.toml`, `D:/projects/AI/amibetter/backend/requirements.txt`
- Impact: Version drift risk; unclear which is authoritative; `requirements.txt` line 15 has syntax error (backtick in `langchain==0.1.20\``)
- Fix approach: Choose one dependency management approach (recommend Poetry) and remove the other; fix syntax error

**Tests Directory Empty:**
- Issue: `backend/tests/` directory contains no test files
- Files: `D:/projects/AI/amibetter/backend/tests/` (empty)
- Impact: No automated testing; regressions undetectable; refactoring risky
- Fix approach: Add pytest tests for services and API endpoints

## Known Bugs

**Requirements.txt Syntax Error:**
- Symptoms: `pip install -r requirements.txt` may fail
- Files: `D:/projects/AI/amibetter/backend/requirements.txt:15`
- Trigger: Line reads `langchain==0.1.20\`` with trailing backtick
- Workaround: Manually remove backtick before installing

**Typo in Model Comment:**
- Symptoms: Minor readability issue
- Files: `D:/projects/AI/amibetter/backend/app/models/journal_entry.py:22`
- Trigger: Comment says "Relationahips" instead of "Relationships"
- Workaround: None needed; cosmetic only

## Security Considerations

**Hardcoded Secret Key:**
- Risk: JWT tokens signed with predictable key `"changeme_in_production"` can be forged
- Files: `D:/projects/AI/amibetter/backend/app/core/config.py:8`
- Current mitigation: None; hardcoded default value
- Recommendations: Remove default value; require SECRET_KEY via environment variable; fail startup if missing

**CORS Wildcard in Production Comment:**
- Risk: `allow_origins=["*"]` permits any domain to make authenticated requests
- Files: `D:/projects/AI/amibetter/backend/app/main.py:14`
- Current mitigation: Comment noting "Configure properly in production"
- Recommendations: Use BACKEND_CORS_ORIGINS from config; fail startup if origins list is empty in production

**No Password Strength Validation:**
- Risk: Users can register with weak passwords (single character, common words)
- Files: `D:/projects/AI/amibetter/backend/app/schemas/user.py:12` (UserCreate accepts any password string)
- Current mitigation: None
- Recommendations: Add Pydantic Field with min_length=8; optionally add complexity requirements

**No Input Validation on Text Fields:**
- Risk: Unbounded content_markdown could enable DoS via large payloads; no XSS sanitization
- Files: `D:/projects/AI/amibetter/backend/app/schemas/journal.py:8` (content_markdown has no length limit)
- Current mitigation: None
- Recommendations: Add max_length constraint; sanitize markdown on output if rendered in web context

**No Rate Limiting:**
- Risk: Authentication endpoints vulnerable to brute force; API endpoints vulnerable to abuse
- Files: `D:/projects/AI/amibetter/backend/app/api/v1/auth.py` (login endpoint)
- Current mitigation: None
- Recommendations: Add slowapi or similar rate limiting; especially protect `/auth/login`

**No Refresh Token Implementation:**
- Risk: Long-lived access tokens (8 days per config) increase attack window if compromised
- Files: `D:/projects/AI/amibetter/backend/app/core/config.py:9` (ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 8)
- Current mitigation: None; `/auth/refresh` endpoint not implemented despite being in API spec
- Recommendations: Implement refresh token flow; reduce access token lifetime to 15-60 minutes

**Sensitive .env File May Be Committed:**
- Risk: Database credentials could be exposed in version control
- Files: `D:/projects/AI/amibetter/backend/.env`
- Current mitigation: `.gitignore` exists but unclear if .env is listed
- Recommendations: Verify .env is in .gitignore; use .env.example for template

## Performance Bottlenecks

**SQL Echo Enabled:**
- Problem: `echo=True` logs all SQL statements to stdout
- Files: `D:/projects/AI/amibetter/backend/app/db/session.py:14`
- Cause: Debug logging enabled by default
- Improvement path: Make echo configurable via environment variable; disable in production

**No Database Connection Pooling Configuration:**
- Problem: Default connection pool settings may not scale
- Files: `D:/projects/AI/amibetter/backend/app/db/session.py:12-15`
- Cause: Using default async_sessionmaker without pool_size, max_overflow settings
- Improvement path: Configure pool_size, max_overflow, pool_timeout based on expected load

**No Pagination Count Endpoint:**
- Problem: List endpoints return data but not total count; clients cannot build pagination UI
- Files: `D:/projects/AI/amibetter/backend/app/api/v1/journals.py:28-45`
- Cause: Only returns list, no total_count
- Improvement path: Return `{"items": [...], "total": N, "page": X, "limit": Y}` response schema

**Missing Database Index on Composite Keys:**
- Problem: Journal queries filter by (user_id, entry_date) but no composite index
- Files: `D:/projects/AI/amibetter/backend/alembic/versions/cf60c00cb3e9_initial.py:64-65` (separate indexes on user_id and entry_date)
- Cause: Alembic autogenerated separate single-column indexes
- Improvement path: Add composite index on (user_id, entry_date) for journals; (user_id, score_date) for daily_scores

## Fragile Areas

**User Model DateTime Mapping:**
- Files: `D:/projects/AI/amibetter/backend/app/models/user.py:16-17`
- Why fragile: `Mapped[DateTime]` type annotation is incorrect; should be `Mapped[datetime]` Python type, not SQLAlchemy column type
- Safe modification: Change to `from datetime import datetime` and use `Mapped[datetime]`
- Test coverage: None

**Service Layer Transaction Handling:**
- Files: `D:/projects/AI/amibetter/backend/app/services/user_service.py`, `D:/projects/AI/amibetter/backend/app/services/journal_service.py`, `D:/projects/AI/amibetter/backend/app/services/goal_service.py`
- Why fragile: Each service method calls commit() independently; no support for multi-service transactions
- Safe modification: Consider unit-of-work pattern or pass commit responsibility to caller
- Test coverage: None

**Duplicate get_db Function:**
- Files: `D:/projects/AI/amibetter/backend/app/deps.py:14-16`, `D:/projects/AI/amibetter/backend/app/db/session.py:22-24`
- Why fragile: Two identical implementations; easy to use wrong one; maintenance burden
- Safe modification: Remove from session.py; use only deps.py version
- Test coverage: None

## Scaling Limits

**Single Database Pattern:**
- Current capacity: Unknown; depends on PostgreSQL instance size
- Limit: Single PostgreSQL handles all reads/writes; vector searches with pgvector add CPU load
- Scaling path: Read replicas for query load; consider dedicated vector DB (Pinecone, Weaviate) at scale

**No Async Task Queue Integration:**
- Current capacity: All processing synchronous within request
- Limit: AI pipeline operations will block HTTP requests
- Scaling path: Celery/Redis listed in dependencies but not integrated; implement task queue for AI operations

**No Caching Layer:**
- Current capacity: Every request hits database
- Limit: Repeated reads (user profile, goals) create unnecessary DB load
- Scaling path: Redis listed in dependencies but not integrated; add caching for user data, computed scores

## Dependencies at Risk

**python-jose Maintenance:**
- Risk: python-jose has low maintenance activity; consider alternatives
- Impact: JWT handling depends on this library
- Migration plan: Consider migrating to PyJWT or authlib

**pgvector Version Mismatch:**
- Risk: pyproject.toml specifies `^0.2.4` but requirements.txt specifies `0.3.2`
- Impact: Different behavior between Poetry and pip installs
- Migration plan: Align versions; prefer newer 0.3.x

## Missing Critical Features

**User Goals Not Integrated:**
- Problem: UserGoal model and CRUD exists but not used anywhere
- Blocks: AI scoring should weight metrics by user goals per IMPLEMENTATION_PLAN.md

**Voice Input Not Supported:**
- Problem: Schema supports audio_file_url but no upload endpoint exists
- Blocks: `/journals/voice` endpoint from API spec not implemented

**No User Profile Update Endpoint:**
- Problem: UserService.update() exists but no API route exposes it
- Blocks: Users cannot update their profile or preferences

**No Embedding Generation:**
- Problem: EntryEmbedding model exists but no code generates embeddings
- Blocks: RAG context retrieval for AI scoring

## Test Coverage Gaps

**All Backend Code Untested:**
- What's not tested: Services, API endpoints, models, security functions
- Files: `D:/projects/AI/amibetter/backend/app/services/`, `D:/projects/AI/amibetter/backend/app/api/`, `D:/projects/AI/amibetter/backend/app/core/security.py`
- Risk: Any change could introduce regressions undetected
- Priority: High

**No Integration Tests:**
- What's not tested: API endpoint behavior, database operations, authentication flow
- Files: `D:/projects/AI/amibetter/backend/tests/` (empty)
- Risk: Service interactions and HTTP contracts unverified
- Priority: High

**No Logging Infrastructure:**
- What's not tested: Application observability
- Files: No logging imports found in `D:/projects/AI/amibetter/backend/app/`
- Risk: Production issues difficult to diagnose; no audit trail
- Priority: Medium

---

*Concerns audit: 2026-01-19*
