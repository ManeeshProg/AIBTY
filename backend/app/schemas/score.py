from uuid import UUID
from datetime import date, datetime
from pydantic import BaseModel


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
