from pydantic import BaseModel, Field


class ExtractedActivity(BaseModel):
    """
    A single extracted activity from journal text.

    Categories align with common goal types:
    - productivity: work, deep work, tasks completed
    - fitness: exercise, steps, workouts
    - learning: study time, books read, courses
    - discipline: meditation, journaling, habits
    - well-being: sleep, mood, stress management
    - creativity: writing, art, music
    - social: conversations, networking, relationships
    """
    category: str = Field(
        description="Activity category (productivity, fitness, learning, discipline, well-being, creativity, social)"
    )
    key: str = Field(
        description="Specific metric key (e.g., 'workout_duration', 'hours_deep_work', 'books_read')"
    )
    value: float = Field(
        description="Numeric value for the activity (duration in minutes, count, rating, etc.)"
    )
    evidence: str = Field(
        description="Text snippet from journal that supports this extraction"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score (0-1): 1.0 for explicit numbers, 0.7-0.9 for inferred values"
    )


class ExtractionResult(BaseModel):
    """
    Result of extracting activities from a journal entry.
    Contains all extracted activities and the original text for debugging.
    """
    activities: list[ExtractedActivity] = Field(
        default_factory=list,
        description="List of extracted activities with metrics"
    )
    raw_text: str = Field(
        description="Original journal text (for debugging and validation)"
    )
