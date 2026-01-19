# Technology Stack

**Analysis Date:** 2026-01-19

## Languages

**Primary:**
- Python 3.11+ - Backend API and AI pipeline (`backend/`)
- TypeScript - Mobile application (`mobile/`)

**Secondary:**
- SQL - Database migrations and queries
- Markdown - Journal entry content format

## Runtime

**Backend Environment:**
- Python 3.11+
- ASGI server: Uvicorn 0.29.0

**Mobile Environment:**
- React Native (Expo SDK)
- Expected: Node.js 18+

**Package Managers:**
- Backend: pip with requirements.txt (Poetry configured in pyproject.toml but requirements.txt is used)
- Mobile: npm (structure indicates Expo project, no package.json found yet)

**Lockfile:**
- Backend: requirements.txt present (no poetry.lock)
- Mobile: Not present (directory scaffolded only)

## Frameworks

**Core:**
- FastAPI 0.110.3 - REST API framework (`backend/app/main.py`)
- SQLAlchemy 2.0.32 - Async ORM (`backend/app/db/session.py`)
- Pydantic 2.7.4 - Data validation and settings (`backend/app/schemas/`)
- React Native (Expo) - Mobile app framework (`mobile/`)

**AI/ML:**
- LangChain 0.1.20 - LLM orchestration framework (`backend/app/ai_pipeline/`)
- LangChain-community 0.0.38 - Community integrations
- LangChain-core 0.1.52 - Core abstractions
- OpenAI 1.30.5 - OpenAI API client (embeddings, Whisper)
- Anthropic 0.28.1 - Claude API client
- tiktoken 0.7.0 - Token counting

**Database:**
- Alembic 1.13.2 - Database migrations (`backend/alembic/`)
- psycopg2-binary 2.9.9 - PostgreSQL adapter (sync)
- psycopg 3.x - PostgreSQL adapter (async, via psycopg[binary])
- pgvector 0.3.2 - Vector similarity search extension

**Authentication:**
- python-jose 3.3.0 - JWT encoding/decoding (`backend/app/core/security.py`)
- passlib 1.7.4 - Password hashing with bcrypt
- bcrypt 4.1.3 - Bcrypt algorithm implementation

**Task Queue:**
- Celery 5.4.0 - Distributed task queue (configured but not yet implemented)
- Redis 5.0.7 - Message broker for Celery
- Kombu 5.3.7 - Messaging library for Celery

**Testing:**
- pytest 8.2.2 - Test framework
- pytest-asyncio 0.23.7 - Async test support
- httpx 0.27.0 - Async HTTP client for API testing

**Utilities:**
- python-dotenv 1.0.1 - Environment variable loading
- orjson 3.10.6 - Fast JSON serialization
- python-multipart 0.0.9 - Form/file upload handling
- email-validator 2.2.0 - Email validation for Pydantic

## Key Dependencies

**Critical:**
- fastapi 0.110.3 - Core API framework, all endpoints depend on it
- sqlalchemy 2.0.32 - All database operations use async SQLAlchemy
- anthropic 0.28.1 - Claude is the primary LLM for analysis (per IMPLEMENTATION_PLAN.md)
- openai 1.30.5 - Embeddings (text-embedding-3-small) and Whisper transcription
- pgvector 0.3.2 - Vector similarity search for RAG pipeline

**Infrastructure:**
- celery 5.4.0 - Async AI pipeline execution
- redis 5.0.7 - Celery broker and potential caching
- psycopg 3.x - Async PostgreSQL connectivity

## Configuration

**Environment:**
- Configuration via `.env` file loaded with python-dotenv
- Pydantic BaseSettings for type-safe config (`backend/app/core/config.py`)
- Key env vars:
  - `DATABASE_URL` - PostgreSQL connection string (required)
  - `SECRET_KEY` - JWT signing key (defaults to "changeme_in_production")
  - `ACCESS_TOKEN_EXPIRE_MINUTES` - JWT expiry (default: 8 days)

**Build:**
- `backend/pyproject.toml` - Poetry project definition
- `backend/requirements.txt` - pip-installable dependencies
- `backend/alembic.ini` - Database migration configuration

## Platform Requirements

**Development:**
- Python 3.11+
- PostgreSQL 16 with pgvector extension
- Redis (for Celery)
- Node.js 18+ (for mobile development)

**Production:**
- Deployment target: Not yet configured
- Expected: Container-based (Dockerfile mentioned in plan but not created)
- Database: Supabase PostgreSQL (based on .env DATABASE_URL)
- File storage: S3/GCS planned for audio files (not yet implemented)

## Notes

- Mobile app (`mobile/`) is scaffolded with Expo Router file structure but has no source files yet
- AI pipeline directories (`backend/app/ai_pipeline/agents/`, `prompts/`, `rag/`) are empty - implementation pending
- Test directory (`backend/tests/`) is empty - no tests written yet
- Celery tasks are not yet implemented despite dependencies being installed

---

*Stack analysis: 2026-01-19*
