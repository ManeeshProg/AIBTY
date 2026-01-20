from uuid import UUID
from datetime import date, datetime
from pydantic import BaseModel, Field
from typing import Literal


class ScoreMetricRead(BaseModel):
    id: UUID
    category: str
    score: float
    weight: float
    reasoning: str | None

    model_config = {"from_attributes": True}


class DailyScoreRead(BaseModel):
    id: UUID
    user_id: UUID
    score_date: date
    verdict: str
    composite_score: float
    summary: str | None
    actionable_advice: str | None
    comparison_data: dict
    created_at: datetime
    metrics: list[ScoreMetricRead] = []

    model_config = {"from_attributes": True}


# Request/Response schemas for scoring endpoints

class ScoreRequest(BaseModel):
    """Request to trigger scoring for a specific date."""
    score_date: date = Field(default_factory=date.today, description="Date to score")


class DailyScoreCreate(BaseModel):
    """Schema for creating a daily score record."""
    score_date: date
    verdict: Literal["better", "same", "worse", "first_day"]
    composite_score: float = Field(ge=0, le=100)
    summary: str | None = None
    actionable_advice: str | None = None
    comparison_data: dict = {}


class StreakInfo(BaseModel):
    """Information about a goal's streak."""
    category: str
    current_streak: int = Field(ge=0, description="Current consecutive improvement days")
    longest_streak: int = Field(ge=0, description="All-time longest streak")
    last_improvement_date: date | None = Field(None, description="Most recent improvement")


class ScoreComparison(BaseModel):
    """Comparison data for scoring."""
    today: float = Field(ge=0, le=100)
    yesterday: float | None = Field(None, ge=0, le=100)
    delta: float | None = None
    verdict: Literal["better", "same", "worse", "first_day"]


class GoalScoreDetail(BaseModel):
    """Detailed score for a single goal."""
    category: str
    base_score: float = Field(ge=0, le=100, description="Deterministic score")
    enhanced_score: float = Field(ge=0, le=100, description="LLM-enhanced score")
    adjustment: float = Field(description="LLM adjustment applied")
    weight: float = Field(gt=0, description="Goal weight")
    weighted_score: float = Field(ge=0, le=100, description="Final weighted score")
    showed_up: bool
    effort_level: str
    evidence: list[str] = []
    reasoning: str
    adjustment_reasoning: str


class ScoringResponse(BaseModel):
    """Complete response from scoring operation."""
    score_date: date
    verdict: Literal["better", "same", "worse", "first_day"]
    composite_score: float = Field(ge=0, le=100)
    comparison: ScoreComparison
    goal_scores: list[GoalScoreDetail]
    streaks: list[StreakInfo] = []


class StreakResponse(BaseModel):
    """Response containing all goal streaks."""
    streaks: list[StreakInfo]
