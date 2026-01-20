import instructor
from anthropic import Anthropic
from app.ai_pipeline.schemas.extraction import ExtractionResult
from app.core.config import settings


class ExtractionAgent:
    """
    Claude-based agent for extracting structured activities from journal text.

    Uses instructor library for automatic Pydantic parsing and retry logic.
    """

    def __init__(self, api_key: str | None = None):
        """
        Initialize extraction agent with Anthropic API key.

        Args:
            api_key: Anthropic API key. Defaults to settings.ANTHROPIC_API_KEY
        """
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is required. Set it in environment or pass to constructor."
            )

        # Patch Anthropic client with instructor for structured outputs
        self.client = instructor.from_anthropic(Anthropic(api_key=self.api_key))

    def extract(self, text: str) -> ExtractionResult:
        """
        Extract structured activities from journal entry text.

        Uses Claude Sonnet 4 to identify activities with numeric values,
        categorize them, and provide evidence and confidence scores.

        Args:
            text: Journal entry content (markdown)

        Returns:
            ExtractionResult with list of ExtractedActivity objects
        """
        system_prompt = """You are an expert at extracting structured, quantifiable activities from personal journal entries.

Your task is to identify activities mentioned in the journal text and extract them with:
1. Category (productivity, fitness, learning, discipline, well-being, creativity, social)
2. Key (specific metric name like 'workout_duration', 'hours_deep_work', 'books_read')
3. Value (numeric value - duration in minutes, count, rating on scale)
4. Evidence (the exact text snippet that supports this extraction)
5. Confidence (0-1 score: use 1.0 for explicit numbers, 0.7-0.9 for inferred/estimated values)

Guidelines:
- Extract ALL quantifiable activities mentioned
- Convert time mentions to minutes (e.g., "2 hours" → 120)
- For implicit activities, estimate reasonable values (e.g., "quick workout" → ~20-30 minutes, confidence 0.7)
- Include evidence text that clearly shows where you got the information
- Focus on activities that can be measured or counted
- If multiple related activities, create separate extractions (e.g., "ran 5 miles in 45 minutes" → distance AND duration)

Categories:
- productivity: work sessions, tasks completed, focus time, meetings
- fitness: workouts, steps, running distance, gym time
- learning: study time, courses, books read, lessons
- discipline: meditation, journaling, habit tracking, routines
- well-being: sleep hours, mood ratings, stress management, therapy
- creativity: writing time, art projects, music practice, creative work
- social: conversations, networking events, quality time with others"""

        user_prompt = f"Extract all quantifiable activities from this journal entry:\n\n{text}"

        # Use instructor to get structured output with automatic retries
        result = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            temperature=0.2,  # Lower temperature for more consistent extraction
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            response_model=ExtractionResult,
        )

        return result
