from datetime import date

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status

from app.deps import CurrentUser, DbSession
from app.schemas.voice import VoiceTranscribeResponse
from app.services.journal_service import JournalService
from app.services.transcription_service import TranscriptionService, SUPPORTED_AUDIO_TYPES

router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/transcribe", response_model=VoiceTranscribeResponse)
async def transcribe_audio(
    db: DbSession,
    current_user: CurrentUser,
    audio: UploadFile = File(..., description="Audio file to transcribe"),
    entry_date: date | None = Query(
        default=None,
        description="Journal entry date (defaults to today)",
    ),
):
    """
    Transcribe audio file and append to journal entry.

    Accepts audio files (mp3, mp4, wav, webm, m4a, etc.) and transcribes
    using OpenAI Whisper API. The transcribed text is appended to the
    journal entry for the specified date (or today if not specified).

    Multiple voice uploads in one day accumulate - existing journal content
    is preserved and new transcription is appended.
    """
    # Validate content type
    content_type = audio.content_type or ""
    if content_type not in SUPPORTED_AUDIO_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported audio format: {content_type}. "
                   f"Supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm",
        )

    # Use today if no date specified
    if entry_date is None:
        entry_date = date.today()

    # Transcribe audio
    transcription_service = TranscriptionService()
    transcribed_text = await transcription_service.transcribe(audio)

    # Append to journal
    journal_service = JournalService(db)
    journal = await journal_service.append_content(
        user_id=current_user.id,
        entry_date=entry_date,
        new_content=transcribed_text,
        input_source="voice",
    )

    return VoiceTranscribeResponse(
        transcribed_text=transcribed_text,
        journal_id=journal.id,
        entry_date=journal.entry_date,
        message="Transcription added to journal",
    )
