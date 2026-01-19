# Coding Conventions

**Analysis Date:** 2026-01-19

## Naming Patterns

**Files:**
- Python modules: `snake_case.py` (e.g., `user_service.py`, `journal_entry.py`)
- SQLAlchemy models: Singular noun, snake_case file (e.g., `user.py`, `daily_score.py`)
- Pydantic schemas: Feature-based grouping (e.g., `user.py`, `journal.py`)
- API routers: Plural resource name (e.g., `journals.py`, `goals.py`)

**Functions:**
- Use `snake_case` for all function names
- Async functions: Prefix with action verb (e.g., `get_by_date`, `create_or_update`, `verify_token`)
- Service methods: CRUD-style naming (`get_by_id`, `get_by_email`, `create`, `update`, `delete`, `list`)

**Variables:**
- Use `snake_case` for all variables
- Database sessions: `db`
- Current user: `current_user`
- Input models: `*_in` suffix (e.g., `user_in`, `goal_in`, `journal_in`)

**Types/Classes:**
- SQLAlchemy models: `PascalCase`, singular noun (e.g., `User`, `JournalEntry`, `DailyScore`)
- Pydantic schemas: `PascalCase` with suffix pattern:
  - `*Base` - shared fields (e.g., `UserBase`, `JournalBase`)
  - `*Create` - creation payload (e.g., `UserCreate`, `GoalCreate`)
  - `*Update` - update payload with optional fields (e.g., `UserUpdate`, `GoalUpdate`)
  - `*Read` - response model (e.g., `UserRead`, `JournalRead`)
- Services: `*Service` suffix (e.g., `UserService`, `JournalService`, `GoalService`)

**Constants:**
- Use `SCREAMING_SNAKE_CASE` in settings (e.g., `PROJECT_NAME`, `API_V1_STR`, `SECRET_KEY`)

## Code Style

**Formatting:**
- No explicit formatter config detected
- Use standard Python formatting (PEP 8 style)
- Indentation: 4 spaces

**Linting:**
- No explicit linter config detected
- Recommend adding `ruff` or `flake8` for consistency

## Import Organization

**Order:**
1. Standard library imports (e.g., `uuid`, `datetime`, `typing`)
2. Third-party imports (e.g., `fastapi`, `sqlalchemy`, `pydantic`)
3. Local application imports (e.g., `from app.core.config import settings`)

**Path Style:**
- Absolute imports from `app` package: `from app.models.user import User`
- Relative imports within same package: `from .user import User` (in `__init__.py`)

**Examples from codebase:**
```python
# From backend/app/api/v1/auth.py
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from app.deps import DbSession, CurrentUser
from app.schemas.user import UserCreate, UserRead
from app.schemas.token import Token
from app.core.security import create_access_token
from app.services.user_service import UserService
```

## Type Annotations

**Pattern:** Use modern Python 3.11+ type hints throughout

**Union types:**
- Use `|` syntax: `str | None`, `User | None`
- Not `Optional[str]` or `Union[str, None]`

**Collections:**
- Use lowercase generics: `list[JournalRead]`, `dict[str, Any]`
- Not `List[JournalRead]` or `Dict[str, Any]`

**FastAPI dependencies:**
- Use `Annotated` for dependency injection:
```python
from typing import Annotated
from fastapi import Depends

DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
```

**SQLAlchemy models:**
- Use `Mapped[T]` with `mapped_column()`:
```python
id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
preferences: Mapped[dict] = mapped_column(JSON, default={})
```

## Error Handling

**HTTP Exceptions:**
- Use FastAPI's `HTTPException` with explicit status codes
- Import status codes: `from fastapi import status`
- Use `status.HTTP_*` constants, not raw integers

**Pattern:**
```python
from fastapi import HTTPException, status

# Authentication errors
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

# Not found errors
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Journal entry not found",
)

# Validation/conflict errors
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Email already registered",
)
```

**Service layer:**
- Return `None` for not-found cases (don't raise)
- Let API layer decide on exception handling
- Example from `backend/app/services/user_service.py`:
```python
async def get_by_email(self, email: str) -> User | None:
    result = await self.db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()
```

## Logging

**Framework:** Not explicitly configured

**Current state:**
- SQLAlchemy engine has `echo=True` for SQL logging
- No application-level logging configured

**Recommendation:**
- Add `loguru` or configure standard `logging` module
- Log at service layer boundaries

## Comments

**Docstrings:**
- Endpoint docstrings: Short one-liner describing the action
```python
@router.get("/{entry_date}", response_model=JournalRead)
async def get_journal(...):
    """Get a specific journal entry by date."""
```

**Inline comments:**
- Used for enum values and data explanations:
```python
input_source: Mapped[str] = mapped_column(String, default="text") # text | voice
verdict: Mapped[str] = mapped_column(String) # better | same | worse
```

## Function Design

**Size:**
- Keep functions focused and concise
- Service methods: single responsibility (one CRUD operation)
- API endpoints: delegate to service layer

**Parameters:**
- Use keyword arguments for optional parameters
- Use `Annotated` for FastAPI dependencies
- Default values at end of parameter list

**Return Values:**
- Explicit return type annotations
- Return `None` for not-found queries
- Return model instance after create/update operations

**Service Pattern:**
```python
class JournalService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: UUID, entry_date: date, content_markdown: str) -> JournalEntry:
        journal = JournalEntry(...)
        self.db.add(journal)
        await self.db.commit()
        await self.db.refresh(journal)
        return journal
```

## Module Design

**Exports:**
- Use `__init__.py` for barrel exports in models and schemas:
```python
# backend/app/models/__init__.py
from .user import User
from .journal_entry import JournalEntry, ExtractedMetric
from .daily_score import DailyScore, ScoreMetric
from .goal import UserGoal
from .embedding import EntryEmbedding
```

**API Routers:**
- Each router module defines `router = APIRouter(prefix="/resource", tags=["resource"])`
- Central router aggregates in `backend/app/api/v1/router.py`

## Pydantic Schemas

**Model Config:**
- Use `model_config` dict (Pydantic v2 style):
```python
class UserRead(UserBase):
    id: UUID
    preferences: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
```

**Inheritance Pattern:**
- `*Base` defines shared required fields
- `*Create` extends Base (often just `pass`)
- `*Update` has all optional fields for partial updates
- `*Read` extends Base, adds id and timestamps

## SQLAlchemy Models

**Table naming:**
- Plural, snake_case: `users`, `journal_entries`, `daily_scores`, `user_goals`

**Primary keys:**
- UUID type with `default=uuid.uuid4`

**Timestamps:**
- `created_at` with `server_default=func.now()`
- `updated_at` with `onupdate=func.now()` and `server_default=func.now()`

**Relationships:**
- Bidirectional with `back_populates`
- Cascade deletes: `cascade="all, delete-orphan"` on parent side

**Foreign Keys:**
- Always indexed: `index=True`

---

*Convention analysis: 2026-01-19*
