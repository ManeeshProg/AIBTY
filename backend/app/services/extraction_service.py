from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.journal_entry import JournalEntry, ExtractedMetric
from app.models.goal import UserGoal, GoalActivityLink
from app.ai_pipeline.agents.extraction_agent import ExtractionAgent
from app.ai_pipeline.schemas.extraction import GoalSuggestion


class ExtractionService:
    """
    Service for extracting structured activities from journal entries
    and persisting them to the database.

    Uses ExtractionAgent (Claude + instructor) to identify and extract
    quantifiable activities from journal text.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize extraction service with database session.

        Args:
            db: SQLAlchemy async session for database operations
        """
        self.db = db

    async def extract_and_persist(self, entry: JournalEntry, map_goals: bool = True) -> list[ExtractedMetric]:
        """
        Extract activities from journal entry and persist to database.

        This method:
        1. Uses ExtractionAgent to extract structured activities from entry text
        2. Creates ExtractedMetric records for each activity
        3. Persists to database and returns the metrics
        4. Optionally maps metrics to user goals

        Args:
            entry: JournalEntry to extract activities from
            map_goals: Whether to create GoalActivityLink records (default: True)

        Returns:
            List of ExtractedMetric records created
        """
        # Instantiate extraction agent
        agent = ExtractionAgent()

        # Extract activities from journal content
        result = agent.extract(entry.content_markdown)

        # Convert each extracted activity to ExtractedMetric
        metrics = []
        for activity in result.activities:
            metric = ExtractedMetric(
                entry_id=entry.id,
                category=activity.category,
                key=activity.key,
                value=activity.value,
                evidence=activity.evidence,
                confidence=activity.confidence,
            )
            self.db.add(metric)
            metrics.append(metric)

        # Commit all metrics at once
        await self.db.commit()

        # Refresh to get database-assigned IDs
        for metric in metrics:
            await self.db.refresh(metric)

        # Optionally map to goals
        if map_goals:
            await self.map_metrics_to_goals(entry.user_id, metrics)

        return metrics

    async def get_metrics_for_entry(self, entry_id: UUID) -> list[ExtractedMetric]:
        """
        Retrieve all extracted metrics for a specific journal entry.

        Args:
            entry_id: UUID of the journal entry

        Returns:
            List of ExtractedMetric records for the entry
        """
        result = await self.db.execute(
            select(ExtractedMetric).where(ExtractedMetric.entry_id == entry_id)
        )
        return list(result.scalars().all())

    async def clear_metrics_for_entry(self, entry_id: UUID) -> None:
        """
        Delete all extracted metrics for a specific journal entry.

        Useful for re-extraction when entry content is updated.

        Args:
            entry_id: UUID of the journal entry
        """
        await self.db.execute(
            delete(ExtractedMetric).where(ExtractedMetric.entry_id == entry_id)
        )
        await self.db.commit()

    async def map_metrics_to_goals(self, user_id: UUID, metrics: list[ExtractedMetric]) -> list[GoalActivityLink]:
        """
        Map extracted metrics to user's active goals.

        Creates GoalActivityLink records for metrics that match user goals based on:
        1. Category exact match (metric.category == goal.category)
        2. Keyword fuzzy match (metric.key contains words from goal.description)

        Args:
            user_id: UUID of the user
            metrics: List of ExtractedMetric to map to goals

        Returns:
            List of GoalActivityLink records created
        """
        # Fetch user's active goals
        result = await self.db.execute(
            select(UserGoal).where(
                UserGoal.user_id == user_id,
                UserGoal.is_active == True
            )
        )
        goals = list(result.scalars().all())

        # Create links for matching metrics and goals
        links = []
        for metric in metrics:
            for goal in goals:
                match_reason = None
                contribution_score = 0.0

                # Primary match: category exact match
                if metric.category.lower() == goal.category.lower():
                    match_reason = f"Category match: {goal.category}"
                    contribution_score = 1.0

                # Secondary match: keyword fuzzy match
                elif self._fuzzy_match(metric.key, goal.description):
                    match_reason = f"Keyword match: {metric.key} in '{goal.description}'"
                    contribution_score = 0.7

                # Create link if match found
                if match_reason:
                    link = GoalActivityLink(
                        goal_id=goal.id,
                        metric_id=metric.id,
                        match_reason=match_reason,
                        contribution_score=contribution_score,
                    )
                    self.db.add(link)
                    links.append(link)

        # Commit all links at once
        if links:
            await self.db.commit()
            for link in links:
                await self.db.refresh(link)

        return links

    def _fuzzy_match(self, metric_key: str, goal_description: str) -> bool:
        """
        Simple fuzzy matching for keywords.

        Checks if significant words from metric_key appear in goal_description.

        Args:
            metric_key: Key from extracted metric (e.g., "workout_duration")
            goal_description: Description from user goal

        Returns:
            True if significant overlap found
        """
        # Extract meaningful words from metric key (split by underscore and remove short words)
        key_words = [word.lower() for word in metric_key.split('_') if len(word) > 3]
        goal_lower = goal_description.lower()

        # Check if any significant word appears in goal description
        return any(word in goal_lower for word in key_words)

    async def suggest_goals(self, user_id: UUID, lookback_days: int = 30) -> list[GoalSuggestion]:
        """
        Suggest new goals based on recurring patterns in journal entries.

        Analyzes extracted metrics over the lookback period to find patterns
        that don't match existing active goals, then surfaces suggestions.

        Args:
            user_id: UUID of the user
            lookback_days: Number of days to look back (default: 30)

        Returns:
            List of GoalSuggestion objects for unmatched patterns
        """
        # Calculate date threshold
        cutoff_date = datetime.now().date() - timedelta(days=lookback_days)

        # Fetch user's active goals
        goals_result = await self.db.execute(
            select(UserGoal).where(
                UserGoal.user_id == user_id,
                UserGoal.is_active == True
            )
        )
        active_goals = list(goals_result.scalars().all())
        active_categories = {goal.category.lower() for goal in active_goals}

        # Query extracted metrics with aggregation by category and key
        # Group by (category, key) and count frequency
        metrics_result = await self.db.execute(
            select(
                ExtractedMetric.category,
                ExtractedMetric.key,
                func.count(ExtractedMetric.id).label('frequency'),
                func.avg(ExtractedMetric.confidence).label('avg_confidence')
            )
            .join(JournalEntry, ExtractedMetric.entry_id == JournalEntry.id)
            .where(
                JournalEntry.user_id == user_id,
                JournalEntry.entry_date >= cutoff_date
            )
            .group_by(ExtractedMetric.category, ExtractedMetric.key)
            .having(func.count(ExtractedMetric.id) >= 3)  # At least 3 occurrences
        )

        # Build suggestions for unmatched patterns
        suggestions = []
        for row in metrics_result:
            category = row.category
            key = row.key
            frequency = row.frequency
            avg_confidence = row.avg_confidence

            # Skip if category already covered by active goal
            if category.lower() in active_categories:
                continue

            # Generate suggestion
            suggestion = GoalSuggestion(
                category=category,
                suggested_description=self._generate_description(category, key),
                based_on_pattern=f"{key.replace('_', ' ')} mentioned {frequency} times in last {lookback_days} days",
                frequency=frequency,
                confidence=min(0.9, avg_confidence * (frequency / 10))  # Scale by frequency
            )
            suggestions.append(suggestion)

        return suggestions

    def _generate_description(self, category: str, key: str) -> str:
        """
        Generate a human-readable goal description from category and key.

        Args:
            category: Activity category
            key: Metric key (e.g., "workout_duration")

        Returns:
            Suggested goal description
        """
        # Clean up the key for readability
        readable_key = key.replace('_', ' ').title()

        # Category-specific templates
        templates = {
            'productivity': f"Track and improve {readable_key}",
            'fitness': f"Maintain consistent {readable_key}",
            'learning': f"Dedicate time to {readable_key}",
            'discipline': f"Build habit around {readable_key}",
            'well-being': f"Monitor and optimize {readable_key}",
            'creativity': f"Engage regularly in {readable_key}",
            'social': f"Prioritize {readable_key}",
        }

        return templates.get(category.lower(), f"Track {readable_key}")
