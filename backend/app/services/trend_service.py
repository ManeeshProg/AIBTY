from uuid import UUID
from datetime import date, timedelta
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.daily_score import DailyScore, ScoreMetric


class TrendDataPoint:
    """Single day's score data for a goal."""
    def __init__(self, score_date: date, score: float):
        self.date = score_date
        self.score = score


class WeekOverWeekResult:
    """Week comparison calculation result."""
    def __init__(
        self,
        this_week_avg: float | None,
        last_week_avg: float | None,
        percentage_change: float | None,
        trend: str,
    ):
        self.this_week_avg = this_week_avg
        self.last_week_avg = last_week_avg
        self.percentage_change = percentage_change
        self.trend = trend


class TrendService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_goal_trend(
        self, user_id: UUID, goal_category: str, days: int = 7
    ) -> list[TrendDataPoint]:
        """
        Get score trend for a specific goal category over the specified days.

        Returns list of (date, score) pairs ordered by date ascending.
        Missing days are NOT included (sparse data, frontend fills gaps).
        """
        today = date.today()
        start_date = today - timedelta(days=days - 1)

        result = await self.db.execute(
            select(DailyScore.score_date, ScoreMetric.score)
            .join(ScoreMetric, ScoreMetric.daily_score_id == DailyScore.id)
            .where(
                and_(
                    DailyScore.user_id == user_id,
                    DailyScore.score_date >= start_date,
                    DailyScore.score_date <= today,
                    ScoreMetric.category == goal_category,
                )
            )
            .order_by(DailyScore.score_date)
        )

        rows = result.all()
        return [TrendDataPoint(score_date=row[0], score=row[1]) for row in rows]

    async def get_all_goals_trends(
        self, user_id: UUID, days: int = 7
    ) -> dict[str, list[TrendDataPoint]]:
        """
        Get trends for all goals the user has scored in one query.

        Returns dict keyed by goal category.
        """
        today = date.today()
        start_date = today - timedelta(days=days - 1)

        result = await self.db.execute(
            select(ScoreMetric.category, DailyScore.score_date, ScoreMetric.score)
            .join(DailyScore, ScoreMetric.daily_score_id == DailyScore.id)
            .where(
                and_(
                    DailyScore.user_id == user_id,
                    DailyScore.score_date >= start_date,
                    DailyScore.score_date <= today,
                )
            )
            .order_by(ScoreMetric.category, DailyScore.score_date)
        )

        rows = result.all()

        trends: dict[str, list[TrendDataPoint]] = {}
        for category, score_date, score in rows:
            if category not in trends:
                trends[category] = []
            trends[category].append(TrendDataPoint(score_date=score_date, score=score))

        return trends

    async def calculate_week_over_week(
        self, user_id: UUID, goal_category: str
    ) -> WeekOverWeekResult:
        """
        Calculate week-over-week comparison for a goal.

        This week: last 7 days (today - 6 to today)
        Last week: 8-14 days ago (today - 13 to today - 7)

        Returns percentage change and trend classification:
        - "improving": percentage_change > 5%
        - "declining": percentage_change < -5%
        - "stable": -5% <= percentage_change <= 5%
        - "insufficient_data": either week has no data
        """
        today = date.today()

        # This week: last 7 days
        this_week_start = today - timedelta(days=6)
        this_week_end = today

        # Last week: 8-14 days ago
        last_week_start = today - timedelta(days=13)
        last_week_end = today - timedelta(days=7)

        # Get this week's scores
        this_week_result = await self.db.execute(
            select(ScoreMetric.score)
            .join(DailyScore, ScoreMetric.daily_score_id == DailyScore.id)
            .where(
                and_(
                    DailyScore.user_id == user_id,
                    DailyScore.score_date >= this_week_start,
                    DailyScore.score_date <= this_week_end,
                    ScoreMetric.category == goal_category,
                )
            )
        )
        this_week_scores = [row[0] for row in this_week_result.all()]

        # Get last week's scores
        last_week_result = await self.db.execute(
            select(ScoreMetric.score)
            .join(DailyScore, ScoreMetric.daily_score_id == DailyScore.id)
            .where(
                and_(
                    DailyScore.user_id == user_id,
                    DailyScore.score_date >= last_week_start,
                    DailyScore.score_date <= last_week_end,
                    ScoreMetric.category == goal_category,
                )
            )
        )
        last_week_scores = [row[0] for row in last_week_result.all()]

        # Calculate averages
        this_week_avg = (
            sum(this_week_scores) / len(this_week_scores)
            if this_week_scores
            else None
        )
        last_week_avg = (
            sum(last_week_scores) / len(last_week_scores)
            if last_week_scores
            else None
        )

        # Calculate percentage change and trend
        if this_week_avg is None or last_week_avg is None:
            return WeekOverWeekResult(
                this_week_avg=this_week_avg,
                last_week_avg=last_week_avg,
                percentage_change=None,
                trend="insufficient_data",
            )

        if last_week_avg == 0:
            # Avoid division by zero - if last week was 0, any positive this week is improvement
            percentage_change = 100.0 if this_week_avg > 0 else 0.0
        else:
            percentage_change = ((this_week_avg - last_week_avg) / last_week_avg) * 100

        # Classify trend
        if percentage_change > 5:
            trend = "improving"
        elif percentage_change < -5:
            trend = "declining"
        else:
            trend = "stable"

        return WeekOverWeekResult(
            this_week_avg=round(this_week_avg, 2),
            last_week_avg=round(last_week_avg, 2),
            percentage_change=round(percentage_change, 1),
            trend=trend,
        )
