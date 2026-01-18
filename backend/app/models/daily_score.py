import uuid
from datetime import date
from sqlalchemy import String, Text, Date, ForeignKey, Float, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base import Base

class DailyScore(Base):
    __tablename__ = "daily_scores"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    score_date: Mapped[date] = mapped_column(Date, index=True)
    
    verdict: Mapped[str] = mapped_column(String) # better | same | worse
    composite_score: Mapped[float] = mapped_column(Float) # 0-100
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    actionable_advice: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Store comparison data JSON (e.g. { "yesterday": 80, "avg": 75 })
    comparison_data: Mapped[dict] = mapped_column(JSON, default={})
    
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="daily_scores")
    metrics = relationship("ScoreMetric", back_populates="daily_score", cascade="all, delete-orphan")


class ScoreMetric(Base):
    __tablename__ = "score_metrics"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    daily_score_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("daily_scores.id"), index=True)
    
    category: Mapped[str] = mapped_column(String)
    score: Mapped[float] = mapped_column(Float) # 0-10
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    reasoning: Mapped[str] = mapped_column(Text, nullable=True)
    
    daily_score = relationship("DailyScore", back_populates="metrics")
