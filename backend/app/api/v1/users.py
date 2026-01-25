"""User preferences API endpoint."""
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import CurrentUser, DbSession
from app.schemas.user import UserPreferencesUpdate, UserPreferencesRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/preferences", response_model=UserPreferencesRead)
async def get_my_preferences(current_user: CurrentUser) -> UserPreferencesRead:
    """Get current user's scheduling preferences."""
    return UserPreferencesRead(
        analysis_time=current_user.analysis_time,
        timezone=current_user.timezone
    )


@router.patch("/me/preferences", response_model=UserPreferencesRead)
async def update_my_preferences(
    preferences: UserPreferencesUpdate,
    current_user: CurrentUser,
    db: DbSession,
) -> UserPreferencesRead:
    """Update current user's scheduling preferences."""
    if preferences.analysis_time is not None:
        current_user.analysis_time = preferences.analysis_time
    if preferences.timezone is not None:
        current_user.timezone = preferences.timezone
    await db.commit()
    await db.refresh(current_user)
    return UserPreferencesRead(
        analysis_time=current_user.analysis_time,
        timezone=current_user.timezone
    )
