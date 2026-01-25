import uuid
from datetime import time
from sqlalchemy import String, JSON, DateTime, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=True)
    preferences: Mapped[dict] = mapped_column(JSON, default={})

    # Evening analysis scheduling
    analysis_time: Mapped[time | None] = mapped_column(Time, nullable=True, default=time(21, 0))
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    journal_entries = relationship("JournalEntry", back_populates="user", cascade="all, delete-orphan")
    daily_scores = relationship("DailyScore", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("UserGoal", back_populates="user", cascade="all, delete-orphan")
