from datetime import date
from uuid import UUID

from pydantic import BaseModel


class VoiceTranscribeResponse(BaseModel):
    """Response schema for voice transcription endpoint."""

    transcribed_text: str
    journal_id: UUID
    entry_date: date
    message: str  # e.g., "Transcription added to journal"

    model_config = {"from_attributes": True}
