# Architecture

**Analysis Date:** 2025-01-19

## Pattern Overview

**Overall:** Layered Monolith with Service Pattern (Backend) + File-based Routing (Mobile)

**Key Characteristics:**
- FastAPI backend with clear separation: API routes -> Services -> Models
- Async-first design using SQLAlchemy 2.0 async patterns
- Pydantic schemas for request/response validation (DTOs)
- Dependency injection via FastAPI's `Depends` system
- Planned AI pipeline with agent-based orchestration (scaffolded, not implemented)
- React Native (Expo) mobile app with file-based routing (structure only)

## Layers

**API Layer:**
- Purpose: HTTP request handling, routing, input validation
- Location: `backend/app/api/v1/`
- Contains: FastAPI routers with endpoint definitions
- Depends on: Services, Schemas, Dependencies (`deps.py`)
- Used by: External clients (mobile app)
- Key files:
  - `backend/app/api/v1/router.py` - Main router aggregator
  - `backend/app/api/v1/auth.py` - Authentication endpoints
  - `backend/app/api/v1/journals.py` - Journal CRUD endpoints
  - `backend/app/api/v1/goals.py` - Goals CRUD endpoints

**Service Layer:**
- Purpose: Business logic encapsulation, database operations
- Location: `backend/app/services/`
- Contains: Service classes with async methods
- Depends on: Models, Database session
- Used by: API Layer
- Key files:
  - `backend/app/services/user_service.py` - User CRUD, authentication
  - `backend/app/services/journal_service.py` - Journal operations
  - `backend/app/services/goal_service.py` - Goal management

**Model Layer:**
- Purpose: Database entity definitions (ORM)
- Location: `backend/app/models/`
- Contains: SQLAlchemy ORM models with relationships
- Depends on: Base class from `db/base.py`
- Used by: Services, Alembic migrations
- Key files:
  - `backend/app/models/user.py` - User entity
  - `backend/app/models/journal_entry.py` - JournalEntry, ExtractedMetric
  - `backend/app/models/daily_score.py` - DailyScore, ScoreMetric
  - `backend/app/models/goal.py` - UserGoal
  - `backend/app/models/embedding.py` - EntryEmbedding (pgvector)

**Schema Layer:**
- Purpose: Request/response data transfer objects (DTOs)
- Location: `backend/app/schemas/`
- Contains: Pydantic models for validation and serialization
- Depends on: Pydantic
- Used by: API Layer
- Key files:
  - `backend/app/schemas/user.py` - UserCreate, UserRead, UserUpdate
  - `backend/app/schemas/journal.py` - JournalCreate, JournalRead
  - `backend/app/schemas/goal.py` - GoalCreate, GoalRead
  - `backend/app/schemas/score.py` - DailyScoreRead, ScoreMetricRead
  - `backend/app/schemas/token.py` - Token, TokenPayload

**Core Layer:**
- Purpose: Cross-cutting concerns (config, security)
- Location: `backend/app/core/`
- Contains: Configuration settings, security utilities
- Depends on: External libraries (jose, passlib)
- Used by: All layers
- Key files:
  - `backend/app/core/config.py` - Settings via pydantic-settings
  - `backend/app/core/security.py` - JWT, password hashing

**Database Layer:**
- Purpose: Database connection and session management
- Location: `backend/app/db/`
- Contains: Async SQLAlchemy engine, session factory, base model
- Depends on: SQLAlchemy, config
- Used by: Dependencies, Services
- Key files:
  - `backend/app/db/session.py` - Async engine and session maker
  - `backend/app/db/base.py` - DeclarativeBase for models

**AI Pipeline Layer (Scaffolded):**
- Purpose: AI orchestration for journal analysis and scoring
- Location: `backend/app/ai_pipeline/`
- Contains: Empty directories (not yet implemented)
- Planned subdirectories:
  - `agents/` - Transcription, extraction, scoring, coach agents
  - `rag/` - Embedding and retrieval logic
  - `prompts/` - LLM prompt templates

## Data Flow

**User Authentication Flow:**

1. Client sends credentials to `POST /api/v1/auth/login`
2. `auth.py` router delegates to `UserService.authenticate()`
3. Service queries User model, verifies password via `security.py`
4. Router creates JWT token via `create_access_token()`
5. Token returned to client

**Journal Entry Flow:**

1. Client sends entry to `POST /api/v1/journals/`
2. `journals.py` router extracts current user via `CurrentUser` dependency
3. Dependency chain: `get_current_user()` -> `verify_token()` -> User lookup
4. Router delegates to `JournalService.create_or_update()`
5. Service creates/updates JournalEntry in database
6. Response serialized via `JournalRead` schema

**Planned AI Evaluation Flow (Not Implemented):**

1. Journal entry triggers evaluation task
2. Orchestrator coordinates agents:
   - Transcription (if voice input)
   - RAG context retrieval from pgvector
   - Extraction of metrics from text
   - Scoring based on metrics + historical data
   - Coach agent generates advice
3. DailyScore saved with metrics

**State Management:**
- Backend: Stateless API, all state in PostgreSQL
- Mobile (planned): Local state + React Query for server state sync

## Key Abstractions

**User:**
- Purpose: Represents an authenticated user
- Examples: `backend/app/models/user.py`
- Pattern: Has-many relationships to JournalEntry, DailyScore, UserGoal

**JournalEntry:**
- Purpose: Daily reflection entry (text or transcribed voice)
- Examples: `backend/app/models/journal_entry.py`
- Pattern: Belongs-to User, Has-many ExtractedMetric, EntryEmbedding

**DailyScore:**
- Purpose: AI-generated daily evaluation result
- Examples: `backend/app/models/daily_score.py`
- Pattern: Belongs-to User, Has-many ScoreMetric, stores verdict and advice

**Service Classes:**
- Purpose: Encapsulate business logic per domain
- Examples: `backend/app/services/user_service.py`
- Pattern: Constructor injection of AsyncSession, async methods for CRUD

**Typed Dependencies:**
- Purpose: Type-safe dependency injection
- Examples: `backend/app/deps.py`
- Pattern: `CurrentUser = Annotated[User, Depends(get_current_user)]`

## Entry Points

**Backend Application:**
- Location: `backend/app/main.py`
- Triggers: `uvicorn app.main:app`
- Responsibilities:
  - Creates FastAPI app instance
  - Configures CORS middleware
  - Mounts v1 API router at `/api/v1`
  - Provides `/health` endpoint

**API Router Aggregator:**
- Location: `backend/app/api/v1/router.py`
- Triggers: Included by main.py
- Responsibilities: Aggregates auth, journals, goals routers

**Database Migrations:**
- Location: `backend/alembic/env.py`
- Triggers: `alembic upgrade head`
- Responsibilities: Runs SQLAlchemy migrations against PostgreSQL

**Mobile App (Planned):**
- Location: `mobile/app/_layout.tsx` (not yet created)
- Triggers: Expo start
- Responsibilities: Root layout with auth/navigation providers

## Error Handling

**Strategy:** HTTP exceptions with status codes, no global error middleware yet

**Patterns:**
- Service returns `None` for not-found, router raises `HTTPException(404)`
- Authentication failures raise `HTTPException(401)` with `WWW-Authenticate` header
- Validation errors handled automatically by Pydantic (422 responses)

**Example from `backend/app/api/v1/journals.py`:**
```python
if not journal:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Journal entry not found",
    )
```

## Cross-Cutting Concerns

**Logging:** Not configured (uses default FastAPI/uvicorn logging)

**Validation:** Pydantic schemas at API boundary, SQLAlchemy constraints at DB level

**Authentication:**
- JWT bearer tokens via OAuth2PasswordBearer
- Token verification in `backend/app/deps.py`
- Password hashing with bcrypt via `backend/app/core/security.py`

**Configuration:**
- Environment-based via pydantic-settings
- `.env` file support in `backend/app/core/config.py`
- Key settings: DATABASE_URL, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES

**Database Sessions:**
- Async context manager pattern in `backend/app/deps.py`
- Session-per-request via dependency injection

---

*Architecture analysis: 2025-01-19*
