"""Mood classification schemas for safety-first verdict generation."""
from enum import Enum
from pydantic import BaseModel, Field


class MoodLevel(str, Enum):
    """User emotional state classification."""
    STRUGGLING = "struggling"  # Do not deliver edge, supportive only
    STABLE = "stable"          # Normal messaging, light edge OK
    THRIVING = "thriving"      # Can handle full edge, celebrate wins


class MoodClassification(BaseModel):
    """Result of mood classification from journal content."""
    level: MoodLevel = Field(description="Classified mood level")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence 0-1")
    crisis_flag: bool = Field(
        default=False,
        description="True if crisis indicators detected (self-harm, hopelessness)"
    )
    reasoning: str = Field(description="Brief explanation of classification")

    # Indicators detected
    positive_signals: list[str] = Field(
        default_factory=list,
        description="Positive indicators found in journal"
    )
    negative_signals: list[str] = Field(
        default_factory=list,
        description="Negative indicators found in journal"
    )

    model_config = {"from_attributes": True}
