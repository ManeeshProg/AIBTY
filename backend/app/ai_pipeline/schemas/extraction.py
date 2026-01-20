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


class GoalSuggestion(BaseModel):
    """
    Suggested goal based on recurring patterns in journal entries.

    Surfaced when user consistently logs activities without a matching goal,
    enabling the system to proactively suggest areas for focus.
    """
    category: str = Field(
        description="Suggested goal category (productivity, fitness, learning, etc.)"
    )
    suggested_description: str = Field(
        description="Recommended goal description based on pattern"
    )
    based_on_pattern: str = Field(
        description="Evidence from entries that motivated this suggestion"
    )
    frequency: int = Field(
        description="How many times this pattern appeared in the lookback period"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence that this is a meaningful goal suggestion"
    )
