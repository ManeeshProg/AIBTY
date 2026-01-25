"""AnalysisRun model for tracking analysis executions."""
import uuid
from datetime import date, datetime
from sqlalchemy import String, Date, ForeignKey, DateTime, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base import Base


class AnalysisRun(Base):
    """Tracks each analysis execution for idempotency and debugging."""
    __tablename__ = "analysis_runs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    analysis_date: Mapped[date] = mapped_column(Date, index=True)

    # Status: pending | running | completed | failed
    status: Mapped[str] = mapped_column(String(20), default="pending")

    # Tracking
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Metadata
    entries_processed: Mapped[int] = mapped_column(Integer, default=0)
    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user = relationship("User")

    # Unique constraint: one analysis per user per day
    __table_args__ = (
        UniqueConstraint("user_id", "analysis_date", name="uq_analysis_runs_user_date"),
    )
