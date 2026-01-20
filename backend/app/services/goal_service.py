from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.goal import UserGoal


class GoalService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, goal_id: UUID, user_id: UUID) -> UserGoal | None:
        result = await self.db.execute(
            select(UserGoal).where(
                UserGoal.id == goal_id,
                UserGoal.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list(self, user_id: UUID, active_only: bool = False) -> list[UserGoal]:
        query = select(UserGoal).where(UserGoal.user_id == user_id)
        if active_only:
            query = query.where(UserGoal.is_active == True)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(
        self,
        user_id: UUID,
        category: str,
        description: str,
        target_value: float,
        weight: float = 1.0,
    ) -> UserGoal:
        goal = UserGoal(
            user_id=user_id,
            category=category,
            description=description,
            target_value=target_value,
            weight=weight,
            is_active=True,
        )
        self.db.add(goal)
        await self.db.commit()
        await self.db.refresh(goal)
        return goal

    async def update(
        self,
        goal: UserGoal,
        description: str | None = None,
        target_value: float | None = None,
        weight: float | None = None,
        is_active: bool | None = None,
    ) -> UserGoal:
        if description is not None:
            goal.description = description
        if target_value is not None:
            goal.target_value = target_value
        if weight is not None:
            goal.weight = weight
        if is_active is not None:
            goal.is_active = is_active
        await self.db.commit()
        await self.db.refresh(goal)
        return goal

    async def delete(self, goal: UserGoal) -> None:
        await self.db.delete(goal)
        await self.db.commit()
