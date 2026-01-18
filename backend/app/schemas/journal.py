from uuid import UUID
from datetime import date, datetime
from pydantic import BaseModel


class JournalBase(BaseModel):
    entry_date: date
    content_markdown: str


class JournalCreate(JournalBase):
    pass


class JournalUpdate(BaseModel):
    content_markdown: str


class ExtractedMetricRead(BaseModel):
    id: UUID
    category: str
    key: str
    value: float
    evidence: str | None
    confidence: float

    model_config = {"from_attributes": True}


class JournalRead(JournalBase):
    id: UUID
    user_id: UUID
    audio_file_url: str | None
    input_source: str
    created_at: datetime
    updated_at: datetime
    metrics: list[ExtractedMetricRead] = []

    model_config = {"from_attributes": True}
