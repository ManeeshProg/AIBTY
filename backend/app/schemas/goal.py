from uuid import UUID
from pydantic import BaseModel


class GoalBase(BaseModel):
    category: str
    description: str
    target_value: float
    weight: float = 1.0


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    description: str | None = None
    target_value: float | None = None
    weight: float | None = None
    is_active: bool | None = None


class GoalRead(GoalBase):
    id: UUID
    user_id: UUID
    is_active: bool

    model_config = {"from_attributes": True}


class GoalSuggestionRead(BaseModel):
    """
    API response schema for goal suggestions.

    Surfaced when system detects recurring patterns in journal entries
    that don't match existing goals.
    """
    category: str
    suggested_description: str
    based_on_pattern: str
    frequency: int
    confidence: float
