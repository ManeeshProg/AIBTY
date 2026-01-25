"""Mood classification agent for safety-first verdict generation."""
import instructor
from anthropic import Anthropic
from app.core.config import settings
from app.ai_pipeline.schemas.mood import MoodClassification, MoodLevel
from app.ai_pipeline.prompts.mood_classification import MOOD_CLASSIFICATION_PROMPT


class MoodClassifier:
    """
    Classifies user mood from journal content to determine appropriate feedback tone.

    This is the SAFETY prerequisite for emotional messaging. Mood must be classified
    BEFORE any "edge" is applied to verdict messaging.

    Mood levels:
    - STRUGGLING: Supportive only, no edge
    - STABLE: Normal feedback, light edge OK
    - THRIVING: Full edge, celebrate wins hard

    Crisis flag overrides everything - if detected, always supportive only.
    """

    def __init__(self, api_key: str | None = None):
        """
        Initialize mood classifier with Anthropic API key.

        Args:
            api_key: Anthropic API key. Defaults to settings.ANTHROPIC_API_KEY
        """
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is required. Set it in environment or pass to constructor."
            )

        self.client = instructor.from_anthropic(Anthropic(api_key=self.api_key))
        self.model = "claude-sonnet-4-20250514"

    async def classify(
        self,
        journal_content: str,
        score_context: str | None = None
    ) -> MoodClassification:
        """
        Classify mood from journal content.

        Args:
            journal_content: The journal entry text to analyze
            score_context: Optional context about today's scores

        Returns:
            MoodClassification with level, confidence, and crisis_flag
        """
        prompt = MOOD_CLASSIFICATION_PROMPT.format(
            journal_content=journal_content,
            score_context=score_context or "No score context available"
        )

        # Use instructor for structured output
        result = self.client.chat.completions.create(
            model=self.model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
            response_model=MoodClassification
        )

        return result

    def get_messaging_tier(self, classification: MoodClassification) -> str:
        """
        Determine messaging tier based on classification.

        Returns:
            "supportive_only" - No edge, only encouragement
            "light_edge" - Normal feedback with gentle challenge
            "full_edge" - Can handle direct challenge, celebrate wins hard
        """
        # CRITICAL: Crisis flag always returns supportive_only
        if classification.crisis_flag:
            return "supportive_only"

        return {
            MoodLevel.STRUGGLING: "supportive_only",
            MoodLevel.STABLE: "light_edge",
            MoodLevel.THRIVING: "full_edge"
        }[classification.level]


class MockMoodClassifier:
    """
    Mock mood classifier for testing without API calls.

    Returns predictable classifications based on simple keyword matching.
    """

    def classify(
        self,
        journal_content: str,
        score_context: str | None = None
    ) -> MoodClassification:
        """Mock classification based on keywords (sync for testing)."""
        content_lower = journal_content.lower()

        # Check for crisis indicators
        crisis_keywords = ["self-harm", "suicide", "hopeless", "nothing matters", "what's the point"]
        crisis_flag = any(kw in content_lower for kw in crisis_keywords)

        # Simple keyword-based classification
        struggling_keywords = ["tired", "failed", "missed", "frustrated", "exhausted", "disappointed"]
        thriving_keywords = ["great", "amazing", "crushed it", "killed it", "achieved", "accomplished"]

        negative_signals = [kw for kw in struggling_keywords if kw in content_lower]
        positive_signals = [kw for kw in thriving_keywords if kw in content_lower]

        if crisis_flag or len(negative_signals) > len(positive_signals):
            level = MoodLevel.STRUGGLING
        elif len(positive_signals) > len(negative_signals):
            level = MoodLevel.THRIVING
        else:
            level = MoodLevel.STABLE

        return MoodClassification(
            level=level,
            confidence=0.7,
            crisis_flag=crisis_flag,
            reasoning="Mock classification based on keyword matching",
            positive_signals=positive_signals,
            negative_signals=negative_signals
        )

    def get_messaging_tier(self, classification: MoodClassification) -> str:
        """Same logic as real classifier."""
        if classification.crisis_flag:
            return "supportive_only"

        return {
            MoodLevel.STRUGGLING: "supportive_only",
            MoodLevel.STABLE: "light_edge",
            MoodLevel.THRIVING: "full_edge"
        }[classification.level]
