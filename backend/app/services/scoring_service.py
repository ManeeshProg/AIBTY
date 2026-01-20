"""Scoring service that orchestrates deterministic + LLM scoring."""

from uuid import UUID
from datetime import date, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.daily_score import DailyScore, ScoreMetric
from app.models.goal import UserGoal
from app.models.journal_entry import JournalEntry
from app.ai_pipeline.scoring.deterministic import DeterministicScorer
from app.ai_pipeline.scoring.llm_enhancer import LLMScoreEnhancer, MockLLMScoreEnhancer
from app.schemas.score import (
    ScoringResponse,
    ScoreComparison,
    GoalScoreDetail,
    StreakInfo,
)


class ScoringService:
    """
    Orchestrates the complete scoring workflow:
    1. Deterministic scoring (base scores)
    2. LLM enhancement (contextual adjustment)
    3. Composite score calculation
    4. Comparison with yesterday (verdict)
    5. Streak tracking
    6. Persistence to database
    """

    SAME_THRESHOLD = 5.0  # Within 5 points = "same" verdict

    def __init__(self, db: AsyncSession):
        self.db = db
        self.deterministic_scorer = DeterministicScorer()
        self._llm_enhancer = None  # Lazy init

    def _get_llm_enhancer(self):
        """Lazy initialization of LLM enhancer with fallback to mock."""
        if self._llm_enhancer is None:
            try:
                self._llm_enhancer = LLMScoreEnhancer()
            except ValueError:
                # API key not configured, use mock
                self._llm_enhancer = MockLLMScoreEnhancer()
        return self._llm_enhancer

    async def score_day(
        self,
        user_id: UUID,
        score_date: date,
    ) -> ScoringResponse:
        """
        Complete scoring workflow for a specific date.

        Args:
            user_id: User to score
            score_date: Date to score

        Returns:
            ScoringResponse with verdict, scores, and streaks

        Raises:
            ValueError: If no journal entry exists for the date
        """
        # 1. Get journal entry for the date
        journal = await self._get_journal_entry(user_id, score_date)
        if not journal:
            raise ValueError(f"No journal entry found for {score_date}")

        # 2. Get active goals
        goals = await self._get_active_goals(user_id)
        if not goals:
            raise ValueError("No active goals found for user")

        # 3. Run deterministic scoring
        deterministic_result = self.deterministic_scorer.score_entry(
            journal_content=journal.content_markdown,
            goals=goals
        )

        # 4. Enhance with LLM (if available)
        llm_enhancer = self._get_llm_enhancer()
        goals_with_descriptions = [
            (g.category, g.description, g.target_value)
            for g in goals
        ]
        enhanced_scores = llm_enhancer.enhance_scoring_result(
            result=deterministic_result,
            goals_with_descriptions=goals_with_descriptions,
            journal_content=journal.content_markdown
        )

        # 5. Calculate composite score with goal weights
        goal_details = []
        total_weighted_score = 0.0
        total_weight = 0.0

        for goal, det_score, enh_score in zip(goals, deterministic_result.goal_scores, enhanced_scores):
            weight = goal.weight
            weighted_score = enh_score.adjusted_score * weight
            total_weighted_score += weighted_score
            total_weight += weight

            goal_details.append(GoalScoreDetail(
                category=goal.category,
                base_score=det_score.base_score,
                enhanced_score=enh_score.adjusted_score,
                adjustment=enh_score.adjustment,
                weight=weight,
                weighted_score=weighted_score,
                showed_up=det_score.showed_up,
                effort_level=det_score.effort_level,
                evidence=det_score.evidence,
                reasoning=det_score.reasoning,
                adjustment_reasoning=enh_score.adjustment_reasoning,
            ))

        composite_score = total_weighted_score / total_weight if total_weight > 0 else 0.0

        # 6. Compare with yesterday and determine verdict
        yesterday_score = await self._get_yesterday_score(user_id, score_date)
        comparison = self._calculate_comparison(composite_score, yesterday_score)

        # 7. Calculate streaks
        streaks = await self._calculate_streaks(user_id, score_date, goal_details, comparison.verdict)

        # 8. Persist to database (upsert)
        await self._persist_score(
            user_id=user_id,
            score_date=score_date,
            composite_score=composite_score,
            verdict=comparison.verdict,
            comparison_data={
                "yesterday": yesterday_score,
                "delta": comparison.delta,
            },
            goal_details=goal_details,
        )

        return ScoringResponse(
            score_date=score_date,
            verdict=comparison.verdict,
            composite_score=composite_score,
            comparison=comparison,
            goal_scores=goal_details,
            streaks=streaks,
        )

    async def get_streaks(self, user_id: UUID) -> list[StreakInfo]:
        """
        Get current streak information for all goals.

        Args:
            user_id: User ID

        Returns:
            List of StreakInfo for each goal category
        """
        # Get all goals
        goals = await self._get_active_goals(user_id)

        # Get all daily scores ordered by date
        result = await self.db.execute(
            select(DailyScore)
            .options(selectinload(DailyScore.metrics))
            .where(DailyScore.user_id == user_id)
            .order_by(DailyScore.score_date.desc())
        )
        daily_scores = list(result.scalars().all())

        streaks = []
        for goal in goals:
            streak_info = self._calculate_goal_streak(goal.category, daily_scores)
            streaks.append(streak_info)

        return streaks

    # Private helper methods

    async def _get_journal_entry(self, user_id: UUID, entry_date: date) -> JournalEntry | None:
        """Get journal entry for a specific date."""
        result = await self.db.execute(
            select(JournalEntry).where(
                JournalEntry.user_id == user_id,
                JournalEntry.entry_date == entry_date,
            )
        )
        return result.scalar_one_or_none()

    async def _get_active_goals(self, user_id: UUID) -> list[UserGoal]:
        """Get all active goals for a user."""
        result = await self.db.execute(
            select(UserGoal).where(
                UserGoal.user_id == user_id,
                UserGoal.is_active == True,
            )
        )
        return list(result.scalars().all())

    async def _get_yesterday_score(self, user_id: UUID, today: date) -> float | None:
        """Get yesterday's composite score."""
        yesterday = today - timedelta(days=1)
        result = await self.db.execute(
            select(DailyScore).where(
                DailyScore.user_id == user_id,
                DailyScore.score_date == yesterday,
            )
        )
        yesterday_record = result.scalar_one_or_none()
        return yesterday_record.composite_score if yesterday_record else None

    def _calculate_comparison(
        self,
        today_score: float,
        yesterday_score: float | None,
    ) -> ScoreComparison:
        """Calculate comparison and verdict."""
        if yesterday_score is None:
            return ScoreComparison(
                today=today_score,
                yesterday=None,
                delta=None,
                verdict="first_day",
            )

        delta = today_score - yesterday_score

        # Determine verdict
        if abs(delta) <= self.SAME_THRESHOLD:
            verdict = "same"
        elif delta > 0:
            verdict = "better"
        else:
            verdict = "worse"

        return ScoreComparison(
            today=today_score,
            yesterday=yesterday_score,
            delta=delta,
            verdict=verdict,
        )

    async def _calculate_streaks(
        self,
        user_id: UUID,
        current_date: date,
        goal_details: list[GoalScoreDetail],
        verdict: str,
    ) -> list[StreakInfo]:
        """Calculate streak information for each goal."""
        # Get historical scores
        result = await self.db.execute(
            select(DailyScore)
            .options(selectinload(DailyScore.metrics))
            .where(DailyScore.user_id == user_id)
            .order_by(DailyScore.score_date.desc())
        )
        daily_scores = list(result.scalars().all())

        streaks = []
        for goal_detail in goal_details:
            streak_info = self._calculate_goal_streak(goal_detail.category, daily_scores)
            streaks.append(streak_info)

        return streaks

    def _calculate_goal_streak(
        self,
        category: str,
        daily_scores: list[DailyScore],
    ) -> StreakInfo:
        """
        Calculate streak for a specific goal category.

        A streak continues when the goal's score improved or stayed the same.
        """
        current_streak = 0
        longest_streak = 0
        temp_streak = 0
        last_improvement_date = None

        # Sort by date ascending for streak calculation
        sorted_scores = sorted(daily_scores, key=lambda x: x.score_date)

        prev_score = None
        for daily_score in sorted_scores:
            # Find the metric for this category
            metric = next(
                (m for m in daily_score.metrics if m.category == category),
                None
            )
            if not metric:
                # Category not scored this day, break streak
                temp_streak = 0
                prev_score = None
                continue

            current_score = metric.score

            if prev_score is None:
                # First day
                temp_streak = 1
            elif current_score >= prev_score - self.SAME_THRESHOLD:
                # Improved or maintained (within threshold)
                temp_streak += 1
                last_improvement_date = daily_score.score_date
            else:
                # Declined, reset streak
                temp_streak = 1

            # Update longest streak
            if temp_streak > longest_streak:
                longest_streak = temp_streak

            prev_score = current_score

        # Current streak is the temp streak if it extends to most recent date
        if sorted_scores:
            current_streak = temp_streak
        else:
            current_streak = 0

        return StreakInfo(
            category=category,
            current_streak=current_streak,
            longest_streak=longest_streak,
            last_improvement_date=last_improvement_date,
        )

    async def _persist_score(
        self,
        user_id: UUID,
        score_date: date,
        composite_score: float,
        verdict: str,
        comparison_data: dict,
        goal_details: list[GoalScoreDetail],
    ) -> None:
        """Persist or update daily score and metrics."""
        # Check if score already exists (upsert logic)
        result = await self.db.execute(
            select(DailyScore)
            .options(selectinload(DailyScore.metrics))
            .where(
                DailyScore.user_id == user_id,
                DailyScore.score_date == score_date,
            )
        )
        existing_score = result.scalar_one_or_none()

        if existing_score:
            # Update existing score
            existing_score.composite_score = composite_score
            existing_score.verdict = verdict
            existing_score.comparison_data = comparison_data

            # Delete old metrics and create new ones
            for metric in existing_score.metrics:
                await self.db.delete(metric)
        else:
            # Create new score
            existing_score = DailyScore(
                user_id=user_id,
                score_date=score_date,
                composite_score=composite_score,
                verdict=verdict,
                comparison_data=comparison_data,
            )
            self.db.add(existing_score)

        # Flush to get the daily_score ID
        await self.db.flush()

        # Create metrics
        for goal_detail in goal_details:
            metric = ScoreMetric(
                daily_score_id=existing_score.id,
                category=goal_detail.category,
                score=goal_detail.enhanced_score,
                weight=goal_detail.weight,
                reasoning=f"{goal_detail.reasoning} | LLM: {goal_detail.adjustment_reasoning}",
            )
            self.db.add(metric)

        await self.db.commit()
