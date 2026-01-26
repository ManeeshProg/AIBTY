"""Verdict generation agent using Azure OpenAI with instructor."""
import instructor
from openai import AzureOpenAI
from app.core.config import settings
from app.ai_pipeline.schemas.verdict import Verdict, VerdictInput, VerdictType, ActivityReference, TomorrowAction
from app.ai_pipeline.prompts.verdict_generation import build_verdict_prompt


class VerdictGenerator:
    """
    Generates emotional verdicts with activity-specific messaging.

    Uses Azure OpenAI to create personalized daily verdicts that:
    - Reference specific activities (never generic)
    - Adapt tone based on mood tier
    - Include actionable guidance for tomorrow
    """

    def __init__(self):
        """Initialize with Azure OpenAI credentials from settings."""
        if not settings.AZURE_OPENAI_API_KEY:
            raise ValueError(
                "AZURE_OPENAI_API_KEY is required. Set it in environment."
            )
        azure_client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_API_BASE,
        )
        self.client = instructor.from_openai(azure_client)
        self.deployment = settings.AZURE_OPENAI_DEPLOYMENT

    def generate(
        self,
        verdict_input: VerdictInput,
        tone_tier: str
    ) -> Verdict:
        """
        Generate verdict with emotional messaging.

        Args:
            verdict_input: Score data and activities
            tone_tier: "supportive_only", "light_edge", or "full_edge"

        Returns:
            Complete Verdict with headline, message, activity refs, and actions
        """
        prompt = build_verdict_prompt(
            verdict_type=verdict_input.verdict_type.value,
            today_score=verdict_input.today_score,
            yesterday_score=verdict_input.yesterday_score,
            score_delta=verdict_input.score_delta,
            streak_days=verdict_input.streak_days,
            activities=verdict_input.activities,
            goal_categories=verdict_input.goal_categories,
            tone_tier=tone_tier
        )

        result = self.client.chat.completions.create(
            model=self.deployment,
            messages=[{"role": "user", "content": prompt}],
            response_model=Verdict
        )

        # Inject the tone that was applied for transparency
        result.tone_applied = tone_tier
        return result


class MockVerdictGenerator:
    """
    Mock verdict generator for testing without API calls.

    Returns predictable verdicts based on input.
    """

    def generate(
        self,
        verdict_input: VerdictInput,
        tone_tier: str
    ) -> Verdict:
        """Generate mock verdict based on input."""
        # Create activity references from input activities
        activity_refs = []
        for act in verdict_input.activities[:3]:  # Limit to 3
            activity_refs.append(
                ActivityReference(
                    activity=act.get("activity", "activity"),
                    category=act.get("category", "general"),
                    sentiment="positive" if verdict_input.verdict_type == VerdictType.BETTER else "neutral"
                )
            )

        # Ensure at least one activity reference
        if not activity_refs:
            activity_refs.append(
                ActivityReference(
                    activity="daily check-in",
                    category="general",
                    sentiment="neutral"
                )
            )

        # Generate tone-appropriate messages
        tone_messages = {
            "supportive_only": {
                VerdictType.BETTER: (
                    "You made progress today.",
                    "Every step forward counts. You showed up and that matters. Keep nurturing this momentum."
                ),
                VerdictType.SAME: (
                    "Steady as you go.",
                    "Maintaining is its own kind of progress. You held the line today."
                ),
                VerdictType.WORSE: (
                    "A rest day for your momentum.",
                    "That's okay - even the best have off days. Tomorrow is a fresh start."
                ),
                VerdictType.FIRST_DAY: (
                    "Your journey begins.",
                    "Welcome! Today marks the first step. Showing up is the hardest part, and you did it."
                ),
            },
            "light_edge": {
                VerdictType.BETTER: (
                    "You moved the needle today.",
                    "Nice work showing up. That effort puts you ahead of yesterday. Can you build on it tomorrow?"
                ),
                VerdictType.SAME: (
                    "Holding steady.",
                    "Not bad, not great. Consistency matters, but tomorrow's a chance to push a bit harder."
                ),
                VerdictType.WORSE: (
                    "Not your strongest showing.",
                    "What got in the way? Tomorrow's a chance to get back on track."
                ),
                VerdictType.FIRST_DAY: (
                    "Day one is done.",
                    "You've started. That's more than most. Now let's see what day two brings."
                ),
            },
            "full_edge": {
                VerdictType.BETTER: (
                    "You showed up harder than yesterday.",
                    "This is how you become someone different. Keep this energy."
                ),
                VerdictType.SAME: (
                    "Treading water.",
                    "Same as yesterday means no growth. What's holding you back from pushing harder?"
                ),
                VerdictType.WORSE: (
                    "Remember those goals?",
                    "They didn't take a day off. What happened? Tomorrow, no excuses."
                ),
                VerdictType.FIRST_DAY: (
                    "Day one. Let's see if there's a day two.",
                    "Starting is easy. Continuing is where most people fail. Prove them wrong."
                ),
            },
        }

        messages = tone_messages.get(tone_tier, tone_messages["light_edge"])
        headline, message = messages.get(verdict_input.verdict_type, ("Today happened.", "Check in tomorrow."))

        return Verdict(
            verdict_type=verdict_input.verdict_type,
            headline=headline,
            message=message,
            activity_references=activity_refs,
            tomorrow_actions=[
                TomorrowAction(
                    action="Continue your momentum" if verdict_input.verdict_type == VerdictType.BETTER else "Show up tomorrow",
                    why="Consistency builds habits",
                    related_goal=verdict_input.goal_categories[0] if verdict_input.goal_categories else None
                )
            ],
            tone_applied=tone_tier
        )
