# Testing Patterns

**Analysis Date:** 2026-01-19

## Test Framework

**Runner:**
- pytest 8.2.2
- Config: No `pytest.ini` or `pyproject.toml` [tool.pytest] section detected

**Assertion Library:**
- pytest built-in assertions

**Async Support:**
- pytest-asyncio 0.23.7 for async test support

**HTTP Testing:**
- httpx 0.27.0 for async HTTP client testing (FastAPI TestClient alternative)

**Run Commands:**
```bash
pytest                           # Run all tests
pytest -v                        # Verbose output
pytest --cov=app                 # With coverage (requires pytest-cov)
pytest tests/test_specific.py   # Run specific file
```

## Test File Organization

**Location:**
- Separate `tests/` directory: `backend/tests/`
- Currently empty (no test files exist yet)

**Recommended Naming:**
- `test_*.py` for test files
- `test_` prefix for test functions

**Recommended Structure:**
```
backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Shared fixtures
│   ├── test_auth.py         # Auth endpoint tests
│   ├── test_journals.py     # Journal endpoint tests
│   ├── test_goals.py        # Goal endpoint tests
│   └── services/
│       ├── test_user_service.py
│       ├── test_journal_service.py
│       └── test_goal_service.py
```

## Test Structure

**Recommended Suite Organization:**
```python
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

class TestAuthEndpoints:
    """Tests for authentication endpoints."""

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "testpass123",
            "full_name": "Test User"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient):
        # First registration
        await client.post("/api/v1/auth/register", json={...})
        # Duplicate should fail
        response = await client.post("/api/v1/auth/register", json={...})
        assert response.status_code == 400
```

**Patterns:**
- Group related tests in classes
- Use `@pytest.mark.asyncio` for async tests
- Descriptive test names: `test_<action>_<scenario>`

## Mocking

**Framework:** unittest.mock (standard library) or pytest-mock

**Recommended Patterns:**
```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_service_with_mocked_db():
    mock_db = AsyncMock()
    mock_db.execute.return_value.scalar_one_or_none.return_value = None

    service = UserService(mock_db)
    result = await service.get_by_email("nonexistent@test.com")

    assert result is None
    mock_db.execute.assert_called_once()
```

**What to Mock:**
- External services (OpenAI, Anthropic API calls)
- Database for unit tests (use real DB for integration)
- Time-dependent operations
- Email/notification services

**What NOT to Mock:**
- Pydantic validation
- SQLAlchemy query building
- FastAPI routing logic

## Fixtures and Factories

**Recommended Test Data Pattern:**
```python
# backend/tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.db.base import Base
from app.models import User
from app.core.security import get_password_hash

@pytest.fixture(scope="function")
async def db_session():
    """Create a fresh database for each test."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession)
    async with async_session() as session:
        yield session

@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        full_name="Test User",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
async def auth_headers(test_user: User) -> dict:
    """Get auth headers for authenticated requests."""
    from app.core.security import create_access_token
    token = create_access_token(subject=str(test_user.id))
    return {"Authorization": f"Bearer {token}"}
```

**Location:**
- Shared fixtures: `backend/tests/conftest.py`
- Feature-specific fixtures: in respective test files

## Coverage

**Requirements:** None enforced currently

**Recommended Setup:**
```bash
pip install pytest-cov
pytest --cov=app --cov-report=html --cov-report=term-missing
```

**Target Coverage:**
- Services: 80%+
- API endpoints: 70%+
- Core utilities: 90%+

## Test Types

**Unit Tests:**
- Scope: Individual service methods, utility functions
- Mock database session
- Fast execution
- Example: Test `UserService.authenticate` with mocked DB

**Integration Tests:**
- Scope: API endpoints with real database
- Use SQLite in-memory or test PostgreSQL instance
- Test full request/response cycle
- Example: Test `/api/v1/auth/register` → `/api/v1/auth/login` flow

**E2E Tests:**
- Not configured
- Consider adding for critical user flows (registration, journal submission, score generation)

## Common Patterns

**Async Testing:**
```python
import pytest

@pytest.mark.asyncio
async def test_async_operation():
    result = await some_async_function()
    assert result is not None
```

**Error Testing:**
```python
@pytest.mark.asyncio
async def test_not_found_returns_404(client: AsyncClient, auth_headers: dict):
    response = await client.get(
        "/api/v1/journals/2099-12-31",  # Future date, no entry
        headers=auth_headers
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Journal entry not found"
```

**Database Testing:**
```python
@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    from app.services.user_service import UserService

    service = UserService(db_session)
    user = await service.create(
        email="new@example.com",
        password="securepass",
        full_name="New User"
    )

    assert user.id is not None
    assert user.email == "new@example.com"
    assert user.hashed_password != "securepass"  # Should be hashed
```

**Parametrized Tests:**
```python
@pytest.mark.parametrize("email,expected_valid", [
    ("valid@example.com", True),
    ("invalid-email", False),
    ("", False),
])
def test_email_validation(email: str, expected_valid: bool):
    # Test email validation logic
    pass
```

## Test Database Strategy

**Recommended Approach:**
1. Use SQLite in-memory for fast unit/integration tests
2. Use test PostgreSQL with pgvector for vector embedding tests
3. Create fresh database per test function (not session)

**Database URL for Tests:**
```python
# backend/tests/conftest.py
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# For vector tests (requires PostgreSQL)
TEST_PG_DATABASE_URL = "postgresql+psycopg://test:test@localhost/amibetter_test"
```

## Missing Tests (Priority Areas)

**High Priority:**
- `backend/app/services/user_service.py` - Authentication logic
- `backend/app/api/v1/auth.py` - Registration and login endpoints
- `backend/app/core/security.py` - Token creation and verification

**Medium Priority:**
- `backend/app/services/journal_service.py` - CRUD operations
- `backend/app/services/goal_service.py` - CRUD operations
- API endpoint authorization (user can only access own data)

**Low Priority:**
- Pydantic schema validation (handled by Pydantic)
- SQLAlchemy model definitions

---

*Testing analysis: 2026-01-19*
