"""LLM-based score enhancement using Azure OpenAI via instructor."""

from pydantic import BaseModel, Field, field_validator
from openai import AzureOpenAI
import instructor
from app.core.config import settings
from app.ai_pipeline.scoring.schemas import GoalScoreOutput, ScoringResult
from app.ai_pipeline.scoring.prompts import SCORE_ENHANCEMENT_PROMPT, SCORE_ENHANCEMENT_SYSTEM


class EnhancedScore(BaseModel):
    """LLM-enhanced score with contextual adjustment."""

    original_score: float = Field(description="The deterministic base score")
    adjusted_score: float = Field(ge=0, le=100, description="Score after LLM adjustment")
    adjustment: float = Field(description="Points added/subtracted from base")
    adjustment_reasoning: str = Field(description="Why the adjustment was made")
    confidence: float = Field(ge=0, le=1, default=0.8, description="Confidence in adjustment")

    @field_validator("adjustment")
    @classmethod
    def validate_adjustment_bounds(cls, v: float) -> float:
        """Ensure adjustment is within +/-20 guardrail."""
        if abs(v) > 20:
            # Clamp to bounds
            return 20.0 if v > 0 else -20.0
        return v


class LLMScoreEnhancer:
    """
    Enhances deterministic scores using Azure OpenAI for contextual understanding.

    Uses instructor library for structured outputs with automatic retries.
    Enforces +/-20 point adjustment guardrails.
    """

    def __init__(self):
        """Initialize with Azure OpenAI credentials from settings."""
        if not settings.AZURE_OPENAI_API_KEY:
            raise ValueError("AZURE_OPENAI_API_KEY not configured")

        # Create Azure OpenAI client and wrap with instructor
        azure_client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_API_BASE,
        )
        self.client = instructor.from_openai(azure_client)
        self.deployment = settings.AZURE_OPENAI_DEPLOYMENT

    def enhance_score(
        self,
        goal_score: GoalScoreOutput,
        goal_description: str,
        target_value: float,
        journal_content: str
    ) -> EnhancedScore:
        """
        Enhance a single goal's score using LLM contextual analysis.

        Args:
            goal_score: Deterministic score output
            goal_description: User's goal description
            target_value: Target value for the goal
            journal_content: Full journal entry text

        Returns:
            EnhancedScore with adjustment and reasoning
        """
        # Calculate valid adjustment range
        min_score = max(0, goal_score.base_score - 20)
        max_score = min(100, goal_score.base_score + 20)

        # Format the prompt
        prompt = SCORE_ENHANCEMENT_PROMPT.format(
            category=goal_score.category,
            goal_description=goal_description,
            target_value=target_value,
            journal_content=journal_content,
            base_score=goal_score.base_score,
            showed_up=goal_score.showed_up,
            effort_level=goal_score.effort_level,
            evidence="; ".join(goal_score.evidence) if goal_score.evidence else "None",
            base_reasoning=goal_score.reasoning,
            min_score=min_score,
            max_score=max_score
        )

        # Call Azure OpenAI with instructor for structured output
        full_prompt = f"{SCORE_ENHANCEMENT_SYSTEM}\n\n{prompt}"
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[{"role": "user", "content": full_prompt}],
            response_model=EnhancedScore
        )

        # Enforce guardrails (belt and suspenders)
        adjustment = response.adjusted_score - goal_score.base_score
        if abs(adjustment) > 20:
            # Clamp to guardrail
            adjustment = 20.0 if adjustment > 0 else -20.0
            response.adjusted_score = goal_score.base_score + adjustment
            response.adjustment = adjustment

        response.original_score = goal_score.base_score

        return response

    def enhance_scoring_result(
        self,
        result: ScoringResult,
        goals_with_descriptions: list[tuple[str, str, float]],  # (category, description, target)
        journal_content: str
    ) -> list[EnhancedScore]:
        """
        Enhance all scores in a ScoringResult.

        Args:
            result: Complete deterministic scoring result
            goals_with_descriptions: List of (category, description, target_value) tuples
            journal_content: Full journal entry text

        Returns:
            List of EnhancedScore objects, one per goal
        """
        # Build lookup for goal descriptions
        goal_lookup = {
            cat: (desc, target)
            for cat, desc, target in goals_with_descriptions
        }

        enhanced_scores = []
        for goal_score in result.goal_scores:
            desc, target = goal_lookup.get(
                goal_score.category,
                (goal_score.category, 1.0)
            )

            enhanced = self.enhance_score(
                goal_score=goal_score,
                goal_description=desc,
                target_value=target,
                journal_content=journal_content
            )
            enhanced_scores.append(enhanced)

        return enhanced_scores


class MockLLMScoreEnhancer:
    """
    Mock enhancer for testing without API calls.

    Returns base scores unchanged with mock reasoning.
    """

    def enhance_score(
        self,
        goal_score: GoalScoreOutput,
        goal_description: str,
        target_value: float,
        journal_content: str
    ) -> EnhancedScore:
        """Return base score unchanged."""
        return EnhancedScore(
            original_score=goal_score.base_score,
            adjusted_score=goal_score.base_score,
            adjustment=0.0,
            adjustment_reasoning="Mock: No adjustment made (testing mode)",
            confidence=1.0
        )

    def enhance_scoring_result(
        self,
        result: ScoringResult,
        goals_with_descriptions: list[tuple[str, str, float]],
        journal_content: str
    ) -> list[EnhancedScore]:
        """Enhance all scores (mock)."""
        goal_lookup = {
            cat: (desc, target)
            for cat, desc, target in goals_with_descriptions
        }

        return [
            self.enhance_score(
                gs,
                goal_lookup.get(gs.category, (gs.category, 1.0))[0],
                goal_lookup.get(gs.category, (gs.category, 1.0))[1],
                journal_content
            )
            for gs in result.goal_scores
        ]
