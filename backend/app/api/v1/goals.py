from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from app.deps import DbSession, CurrentUser
from app.schemas.goal import GoalCreate, GoalRead, GoalUpdate
from app.services.goal_service import GoalService

router = APIRouter(prefix="/goals", tags=["goals"])


@router.get("/", response_model=list[GoalRead])
async def list_goals(
    db: DbSession,
    current_user: CurrentUser,
):
    """List all user goals."""
    service = GoalService(db)
    goals = await service.list(current_user.id)
    return goals


@router.post("/", response_model=GoalRead, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal_in: GoalCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Create a new goal."""
    service = GoalService(db)
    goal = await service.create(
        user_id=current_user.id,
        category=goal_in.category,
        description=goal_in.description,
        target_value=goal_in.target_value,
        weight=goal_in.weight,
    )
    return goal


@router.put("/{goal_id}", response_model=GoalRead)
async def update_goal(
    goal_id: UUID,
    goal_in: GoalUpdate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Update an existing goal."""
    service = GoalService(db)
    goal = await service.get_by_id(goal_id, current_user.id)

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )

    updated = await service.update(
        goal,
        description=goal_in.description,
        target_value=goal_in.target_value,
        weight=goal_in.weight,
        is_active=goal_in.is_active,
    )
    return updated


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    """Delete a goal."""
    service = GoalService(db)
    goal = await service.get_by_id(goal_id, current_user.id)

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )

    await service.delete(goal)
