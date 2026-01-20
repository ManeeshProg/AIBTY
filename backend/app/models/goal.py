import uuid
from sqlalchemy import String, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base import Base

class UserGoal(Base):
    __tablename__ = "user_goals"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)

    category: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    target_value: Mapped[float] = mapped_column(Float)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    user = relationship("User", back_populates="goals")


class GoalActivityLink(Base):
    """
    Links extracted metrics (activities) to user goals.

    Enables tracking which journal activities contribute to which goals,
    and surfacing evidence of goal progress.
    """
    __tablename__ = "goal_activity_links"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    goal_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_goals.id"), index=True)
    metric_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("extracted_metrics.id"), index=True)

    match_reason: Mapped[str] = mapped_column(String)  # Why this metric matches this goal
    contribution_score: Mapped[float] = mapped_column(Float, default=1.0)  # How much it contributes

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    goal = relationship("UserGoal", backref="activity_links")
    metric = relationship("ExtractedMetric", backref="goal_links")
