from uuid import UUID
from datetime import date, datetime
from pydantic import BaseModel
from typing import Literal


class TrendDataPoint(BaseModel):
    """Single day's score for a goal."""
    date: date
    score: float  # 0-10 scale (from ScoreMetric)

    model_config = {"from_attributes": True}


class WeekOverWeekComparison(BaseModel):
    """Week comparison result."""
    this_week_avg: float | None  # None if no data
    last_week_avg: float | None  # None if no data
    percentage_change: float | None  # None if can't calculate
    trend: Literal["improving", "declining", "stable", "insufficient_data"]


class GoalTrendRead(BaseModel):
    """Complete trend data for one goal."""
    goal_category: str
    goal_description: str | None  # From UserGoal if available
    data_points: list[TrendDataPoint]
    week_over_week: WeekOverWeekComparison


class TrendsResponse(BaseModel):
    """All goals trends response."""
    user_id: UUID
    generated_at: datetime
    trends: list[GoalTrendRead]
