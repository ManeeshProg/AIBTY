"""Verdict schemas for daily evaluation results."""
from enum import Enum
from pydantic import BaseModel, Field


class VerdictType(str, Enum):
    """Type of daily verdict."""
    BETTER = "better"
    SAME = "same"
    WORSE = "worse"
    FIRST_DAY = "first_day"


class ActivityReference(BaseModel):
    """Specific activity mentioned in verdict."""
    activity: str = Field(description="The specific activity referenced")
    category: str = Field(description="Goal category this relates to")
    sentiment: str = Field(description="positive, neutral, or negative framing")


class TomorrowAction(BaseModel):
    """Concrete actionable guidance for tomorrow."""
    action: str = Field(description="Specific action to take")
    why: str = Field(description="Brief reason this helps")
    related_goal: str | None = Field(default=None, description="Goal category if applicable")


class Verdict(BaseModel):
    """Complete verdict with emotional messaging."""
    verdict_type: VerdictType
    headline: str = Field(description="Short, punchy verdict (1 sentence)")
    message: str = Field(description="Full emotional message (2-4 sentences)")
    activity_references: list[ActivityReference] = Field(
        min_length=1,
        description="Specific activities mentioned - MUST have at least 1"
    )
    tomorrow_actions: list[TomorrowAction] = Field(
        min_length=1,
        description="Actionable guidance for tomorrow - MUST have at least 1"
    )
    tone_applied: str = Field(description="supportive_only, light_edge, or full_edge")


class VerdictInput(BaseModel):
    """Input data for verdict generation."""
    verdict_type: VerdictType
    today_score: float
    yesterday_score: float | None = None
    score_delta: float | None = None
    activities: list[dict] = Field(
        default_factory=list,
        description="Extracted activities with evidence"
    )
    goal_categories: list[str] = Field(default_factory=list)
    streak_days: int = 0
