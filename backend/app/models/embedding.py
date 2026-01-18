import uuid
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from app.db.base import Base

class EntryEmbedding(Base):
    __tablename__ = "entry_embeddings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    entry_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("journal_entries.id"), index=True)
    
    embedding: Mapped[Vector] = mapped_column(Vector(1536)) # OpenAI small embedding dims
    chunk_text: Mapped[str] = mapped_column(Text)
    
    entry = relationship("JournalEntry", back_populates="embeddings")
