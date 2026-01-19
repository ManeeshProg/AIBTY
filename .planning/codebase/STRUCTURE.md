# Codebase Structure

**Analysis Date:** 2025-01-19

## Directory Layout

```
amibetter/
├── backend/                    # FastAPI Python backend
│   ├── alembic/               # Database migrations
│   │   └── versions/          # Migration scripts
│   ├── app/                   # Main application code
│   │   ├── ai_pipeline/       # AI orchestration (scaffolded, empty)
│   │   │   ├── agents/        # AI agents (empty)
│   │   │   ├── prompts/       # LLM prompts (empty)
│   │   │   └── rag/           # Retrieval-augmented generation (empty)
│   │   ├── api/               # API layer
│   │   │   └── v1/            # Version 1 endpoints
│   │   ├── core/              # Cross-cutting (config, security)
│   │   ├── db/                # Database setup
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── schemas/           # Pydantic DTOs
│   │   └── services/          # Business logic
│   ├── scripts/               # Utility scripts
│   ├── tests/                 # Test files (empty)
│   ├── .env                   # Environment variables
│   ├── alembic.ini            # Alembic configuration
│   ├── pyproject.toml         # Poetry configuration
│   └── requirements.txt       # Pip dependencies
│
├── mobile/                    # React Native Expo app (scaffolded, empty)
│   ├── app/                   # Expo Router pages
│   │   ├── (auth)/            # Auth screens (login, register)
│   │   └── (tabs)/            # Main app tabs
│   ├── components/            # Reusable components
│   │   └── ui/                # Primitive UI components
│   ├── hooks/                 # Custom React hooks
│   ├── lib/                   # Utilities (api client, storage)
│   ├── providers/             # Context providers
│   └── types/                 # TypeScript interfaces
│
├── .planning/                 # GSD planning documents
│   └── codebase/              # Codebase analysis docs
├── .claude/                   # Claude Code configuration
├── IMPLEMENTATION_PLAN.md     # Detailed project blueprint
└── README.md                  # Project overview
```

## Directory Purposes

**backend/app/api/v1/:**
- Purpose: HTTP endpoint definitions
- Contains: FastAPI router modules
- Key files:
  - `router.py` - Aggregates all v1 routers
  - `auth.py` - /auth/* endpoints (register, login, me)
  - `journals.py` - /journals/* CRUD endpoints
  - `goals.py` - /goals/* CRUD endpoints

**backend/app/services/:**
- Purpose: Business logic encapsulation
- Contains: Service classes with async methods
- Key files:
  - `user_service.py` - User CRUD, authentication logic
  - `journal_service.py` - Journal CRUD, date-based queries
  - `goal_service.py` - Goal management

**backend/app/models/:**
- Purpose: SQLAlchemy ORM entity definitions
- Contains: Model classes with relationships
- Key files:
  - `user.py` - User model
  - `journal_entry.py` - JournalEntry, ExtractedMetric
  - `daily_score.py` - DailyScore, ScoreMetric
  - `goal.py` - UserGoal
  - `embedding.py` - EntryEmbedding (pgvector)
  - `__init__.py` - Exports all models

**backend/app/schemas/:**
- Purpose: Pydantic request/response schemas
- Contains: Data transfer objects
- Key files:
  - `user.py` - UserCreate, UserRead, UserUpdate
  - `journal.py` - JournalCreate, JournalRead, ExtractedMetricRead
  - `goal.py` - GoalCreate, GoalRead, GoalUpdate
  - `score.py` - DailyScoreRead, ScoreMetricRead
  - `token.py` - Token, TokenPayload

**backend/app/core/:**
- Purpose: Application configuration and security
- Contains: Settings, JWT/password utilities
- Key files:
  - `config.py` - Settings class with env loading
  - `security.py` - create_access_token, verify_token, password hashing

**backend/app/db/:**
- Purpose: Database connection management
- Contains: Engine, session factory, base model
- Key files:
  - `session.py` - Async SQLAlchemy engine and session maker
  - `base.py` - DeclarativeBase for ORM models

**backend/app/ai_pipeline/:**
- Purpose: AI orchestration for journal analysis (not implemented)
- Contains: Empty directories
- Planned structure per IMPLEMENTATION_PLAN.md:
  - `orchestrator.py` - Main coordinator
  - `agents/` - transcription, extraction, scoring, coach agents
  - `rag/` - embedder, retriever
  - `prompts/` - extraction.md, scoring.md, coaching.md

**backend/alembic/:**
- Purpose: Database schema migrations
- Contains: Migration configuration and version scripts
- Key files:
  - `env.py` - Alembic environment setup
  - `versions/` - Migration scripts

**mobile/app/:**
- Purpose: Expo Router file-based routing (not implemented)
- Contains: Empty directories
- Planned structure:
  - `_layout.tsx` - Root layout
  - `(auth)/` - Unprotected auth screens
  - `(tabs)/` - Protected main app screens

## Key File Locations

**Entry Points:**
- `backend/app/main.py`: FastAPI application factory
- `backend/app/api/v1/router.py`: API router aggregation

**Configuration:**
- `backend/app/core/config.py`: Application settings
- `backend/.env`: Environment variables
- `backend/alembic.ini`: Migration configuration

**Core Logic:**
- `backend/app/services/`: All business logic
- `backend/app/deps.py`: Dependency injection (get_db, get_current_user)

**Database:**
- `backend/app/models/`: All ORM models
- `backend/app/db/session.py`: Database connection
- `backend/alembic/versions/`: Migration history

**Testing:**
- `backend/tests/`: Test directory (empty)

## Naming Conventions

**Files:**
- Python modules: `snake_case.py` (e.g., `user_service.py`, `journal_entry.py`)
- TypeScript/React (planned): `PascalCase.tsx` for components, `camelCase.ts` for utils

**Directories:**
- All lowercase with underscores: `ai_pipeline/`, `journal_entry/`
- Expo route groups: Parentheses for grouping `(auth)/`, `(tabs)/`

**Models:**
- Class names: `PascalCase` (e.g., `JournalEntry`, `DailyScore`)
- Table names: `snake_case` plural (e.g., `journal_entries`, `daily_scores`)

**Schemas:**
- Naming pattern: `{Entity}Base`, `{Entity}Create`, `{Entity}Read`, `{Entity}Update`

**Services:**
- Class names: `{Entity}Service` (e.g., `UserService`, `JournalService`)
- File names: `{entity}_service.py`

**API Routers:**
- File names: Plural entity name (e.g., `journals.py`, `goals.py`)
- Router prefix: `/{plural}` (e.g., `/journals`, `/goals`)

## Where to Add New Code

**New API Endpoint:**
- Primary code: `backend/app/api/v1/{resource}.py`
- Add router to: `backend/app/api/v1/router.py`
- Create schema: `backend/app/schemas/{resource}.py`
- Create service: `backend/app/services/{resource}_service.py`

**New Database Model:**
- Implementation: `backend/app/models/{entity}.py`
- Export in: `backend/app/models/__init__.py`
- Create migration: `alembic revision --autogenerate -m "description"`

**New Service:**
- Implementation: `backend/app/services/{entity}_service.py`
- Follow pattern: Constructor takes `AsyncSession`, async methods

**New Pydantic Schema:**
- Implementation: `backend/app/schemas/{entity}.py`
- Export in: `backend/app/schemas/__init__.py`
- Follow pattern: Base, Create, Read, Update classes

**New AI Agent (when implementing):**
- Implementation: `backend/app/ai_pipeline/agents/{agent_name}_agent.py`
- Prompts: `backend/app/ai_pipeline/prompts/{agent_name}.md`

**New Mobile Screen (when implementing):**
- Route file: `mobile/app/(tabs)/{screen}.tsx` or `mobile/app/(auth)/{screen}.tsx`
- Layout: `mobile/app/{group}/_layout.tsx`

**New Mobile Component:**
- Reusable: `mobile/components/{ComponentName}.tsx`
- Primitive UI: `mobile/components/ui/{ComponentName}.tsx`

**New Mobile Hook:**
- Implementation: `mobile/hooks/use{Feature}.ts`

## Special Directories

**backend/alembic/versions/:**
- Purpose: Database migration scripts
- Generated: Yes (via `alembic revision --autogenerate`)
- Committed: Yes

**backend/__pycache__/ and *.pyc:**
- Purpose: Python bytecode cache
- Generated: Yes
- Committed: No (in .gitignore)

**mobile/node_modules/ (when created):**
- Purpose: NPM dependencies
- Generated: Yes (via `npm install`)
- Committed: No

**.planning/codebase/:**
- Purpose: GSD codebase analysis documents
- Generated: By codebase mappers
- Committed: Yes

**backend/.env:**
- Purpose: Environment variables (secrets)
- Generated: Manual
- Committed: No (contains DATABASE_URL, SECRET_KEY)

---

*Structure analysis: 2025-01-19*
