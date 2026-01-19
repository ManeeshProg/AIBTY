from fastapi import UploadFile, HTTPException, status
from openai import AsyncOpenAI

from app.core.config import settings

# Supported audio formats for Whisper API
SUPPORTED_AUDIO_TYPES = {
    "audio/mpeg",      # mp3
    "audio/mp4",       # mp4
    "audio/x-m4a",     # m4a
    "audio/mp4a-latm", # m4a alternate
    "audio/wav",       # wav
    "audio/x-wav",     # wav alternate
    "audio/webm",      # webm
    "audio/mpga",      # mpga
    "video/mp4",       # mp4 video (has audio track)
    "video/webm",      # webm video (has audio track)
}


class TranscriptionService:
    """Service for transcribing audio files using OpenAI Whisper API."""

    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OpenAI API key not configured",
            )
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def transcribe(self, audio_file: UploadFile) -> str:
        """
        Transcribe audio file using OpenAI Whisper API.

        Args:
            audio_file: FastAPI UploadFile containing audio data

        Returns:
            Transcribed text string

        Raises:
            HTTPException: If transcription fails or unsupported format
        """
        # Validate content type
        content_type = audio_file.content_type or ""
        if content_type not in SUPPORTED_AUDIO_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported audio format: {content_type}. "
                       f"Supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm",
            )

        try:
            # Read file content
            audio_bytes = await audio_file.read()

            # Create a file-like tuple for OpenAI API
            # Format: (filename, content, content_type)
            file_tuple = (
                audio_file.filename or "audio.mp3",
                audio_bytes,
                content_type,
            )

            # Call Whisper API
            transcription = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=file_tuple,
            )

            return transcription.text

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Transcription failed: {str(e)}",
            )
