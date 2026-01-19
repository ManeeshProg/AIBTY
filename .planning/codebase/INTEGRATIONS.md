# External Integrations

**Analysis Date:** 2026-01-19

## APIs & External Services

**AI/LLM Services:**

- **Anthropic Claude** - Primary LLM for text analysis
  - SDK: `anthropic==0.28.1`
  - Purpose: Journal entry analysis, metric extraction, coaching advice
  - Model: Claude 3.5 Sonnet (per IMPLEMENTATION_PLAN.md)
  - Auth: API key (env var not yet configured)
  - Files: `backend/app/ai_pipeline/agents/` (pending implementation)

- **OpenAI** - Embeddings and transcription
  - SDK: `openai==1.30.5`
  - Purpose 1: Text embeddings for RAG pipeline
  - Model: text-embedding-3-small (1536 dimensions per `backend/app/models/embedding.py`)
  - Purpose 2: Voice transcription
  - Model: Whisper API
  - Auth: API key (env var not yet configured)
  - Files: `backend/app/ai_pipeline/rag/` (pending implementation)

## Data Storage

**Primary Database:**
- PostgreSQL 16 with pgvector extension
  - Provider: Supabase (based on connection string)
  - Connection: `DATABASE_URL` env var
  - Host: `aws-1-ap-south-1.pooler.supabase.com:6543`
  - SSL: Required (`sslmode=require`)
  - Client: SQLAlchemy 2.0 async with psycopg driver
  - Files:
    - `backend/app/db/session.py` - Async engine configuration
    - `backend/app/db/base.py` - Base model class
    - `backend/alembic/` - Migration management

**Vector Store:**
- pgvector extension (integrated with PostgreSQL)
  - Purpose: Semantic search for RAG context retrieval
  - Dimension: 1536 (OpenAI text-embedding-3-small)
  - Table: `entry_embeddings` (`backend/app/models/embedding.py`)

**File Storage:**
- Planned: AWS S3 or Google Cloud Storage
  - Purpose: Audio file storage for voice journal entries
  - Status: Not yet implemented
  - Schema support: `audio_file_url` field in JournalEntry model

**Caching:**
- Redis
  - Package: `redis==5.0.7`
  - Purpose: Celery message broker, potential response caching
  - Status: Dependency installed, not yet configured
  - Connection: Env var not yet defined

## Authentication & Identity

**Auth Provider:** Custom JWT-based authentication

**Implementation:**
- Location: `backend/app/core/security.py`
- JWT library: python-jose
- Algorithm: HS256
- Token expiry: 8 days (default)
- Password hashing: bcrypt via passlib

**Flow:**
1. User registers via `/api/v1/auth/register`
2. User logs in via `/api/v1/auth/login` (OAuth2 password flow)
3. JWT access token returned
4. Token validated via `OAuth2PasswordBearer` dependency

**Key Files:**
- `backend/app/core/security.py` - Token creation/verification, password hashing
- `backend/app/deps.py` - `get_current_user` dependency
- `backend/app/api/v1/auth.py` - Auth endpoints

## Monitoring & Observability

**Error Tracking:**
- Not configured
- Recommendation: Add Sentry integration

**Logs:**
- SQLAlchemy echo mode enabled in development (`echo=True` in session.py)
- Alembic logging configured in `alembic.ini`
- No centralized logging framework

**Health Check:**
- Endpoint: `GET /health`
- Response: `{"status": "healthy"}`
- Location: `backend/app/main.py`

## CI/CD & Deployment

**Hosting:**
- Not yet configured
- Database hosted on Supabase (AWS ap-south-1)

**CI Pipeline:**
- None configured
- No GitHub Actions or similar

**Planned Infrastructure (from IMPLEMENTATION_PLAN.md):**
- Containerization via Docker
- Task queue: Celery with Redis broker
- Object storage: S3/GCS for audio files

## Environment Configuration

**Required env vars (backend):**
```
DATABASE_URL          # PostgreSQL connection string (required)
SECRET_KEY            # JWT signing key (has insecure default)
```

**Planned env vars (not yet used):**
```
ANTHROPIC_API_KEY     # Claude API access
OPENAI_API_KEY        # Embeddings and Whisper
REDIS_URL             # Celery broker
AWS_ACCESS_KEY_ID     # S3 access (for audio storage)
AWS_SECRET_ACCESS_KEY # S3 access (for audio storage)
```

**Secrets location:**
- `backend/.env` - Local development (contains DB credentials)
- Production: Not yet configured

**Security Note:**
- `.env` file contains plaintext database credentials
- `SECRET_KEY` in config.py has insecure default value "changeme_in_production"

## Webhooks & Callbacks

**Incoming:**
- None configured

**Outgoing:**
- None configured

## Task Queue Integration

**Celery (planned, not implemented):**
- Purpose: Async AI pipeline execution
- Broker: Redis
- Tasks: Process journal entries, run AI evaluation
- Packages installed: `celery==5.4.0`, `redis==5.0.7`, `kombu==5.3.7`
- Status: Dependencies present, no task definitions

## Database Tables

Current schema (from models):

| Table | Purpose | Key Relationships |
|-------|---------|-------------------|
| `users` | User accounts | Has journals, scores, goals |
| `journal_entries` | Daily reflections | Belongs to user, has metrics/embeddings |
| `extracted_metrics` | AI-extracted data points | Belongs to journal entry |
| `entry_embeddings` | Vector embeddings (pgvector) | Belongs to journal entry |
| `user_goals` | User-defined objectives | Belongs to user |
| `daily_scores` | AI evaluation results | Belongs to user, has score metrics |
| `score_metrics` | Category-level scores | Belongs to daily score |

**Migration Status:**
- Initial migration applied: `cf60c00cb3e9_initial.py`

---

*Integration audit: 2026-01-19*
