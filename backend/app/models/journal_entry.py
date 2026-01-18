import uuid
from datetime import date
from sqlalchemy import String, Text, Date, ForeignKey, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base import Base

class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    entry_date: Mapped[date] = mapped_column(Date, index=True)
    
    content_markdown: Mapped[str] = mapped_column(Text)
    audio_file_url: Mapped[str] = mapped_column(String, nullable=True)
    input_source: Mapped[str] = mapped_column(String, default="text") # text | voice
    
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationahips
    user = relationship("User", back_populates="journal_entries")
    metrics = relationship("ExtractedMetric", back_populates="entry", cascade="all, delete-orphan")
    embeddings = relationship("EntryEmbedding", back_populates="entry", cascade="all, delete-orphan")


class ExtractedMetric(Base):
    __tablename__ = "extracted_metrics"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    entry_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("journal_entries.id"), index=True)
    
    category: Mapped[str] = mapped_column(String, index=True) # productivity, learning, etc
    key: Mapped[str] = mapped_column(String) # e.g. hours_deep_work
    value: Mapped[float] = mapped_column(Float)
    evidence: Mapped[str] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    
    entry = relationship("JournalEntry", back_populates="metrics")
