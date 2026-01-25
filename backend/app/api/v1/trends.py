from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Query

from app.deps import DbSession, CurrentUser
from app.schemas.trend import (
    TrendDataPoint,
    WeekOverWeekComparison,
    GoalTrendRead,
    TrendsResponse,
)
from app.services.trend_service import TrendService
from app.services.goal_service import GoalService

router = APIRouter(prefix="/trends", tags=["trends"])


@router.get("/", response_model=TrendsResponse)
async def get_all_trends(
    db: DbSession,
    current_user: CurrentUser,
    days: int = Query(default=7, ge=1, le=30, description="Number of days for trend data"),
):
    """
    Get score trends for all user goals.

    Returns trend data points and week-over-week comparison for each goal
    that has been scored. Data is structured for mobile visualization.
    """
    trend_service = TrendService(db)
    goal_service = GoalService(db)

    # Get all goals for descriptions
    goals = await goal_service.list(current_user.id)
    goal_descriptions = {g.category: g.description for g in goals}

    # Get trends for all scored categories
    all_trends = await trend_service.get_all_goals_trends(current_user.id, days)

    trends_list: list[GoalTrendRead] = []
    for category, data_points in all_trends.items():
        # Calculate week-over-week for this category
        wow = await trend_service.calculate_week_over_week(current_user.id, category)

        trends_list.append(
            GoalTrendRead(
                goal_category=category,
                goal_description=goal_descriptions.get(category),
                data_points=[
                    TrendDataPoint(date=dp.date, score=dp.score)
                    for dp in data_points
                ],
                week_over_week=WeekOverWeekComparison(
                    this_week_avg=wow.this_week_avg,
                    last_week_avg=wow.last_week_avg,
                    percentage_change=wow.percentage_change,
                    trend=wow.trend,
                ),
            )
        )

    return TrendsResponse(
        user_id=current_user.id,
        generated_at=datetime.now(),
        trends=trends_list,
    )


@router.get("/{goal_category}", response_model=GoalTrendRead)
async def get_goal_trend(
    goal_category: str,
    db: DbSession,
    current_user: CurrentUser,
    days: int = Query(default=7, ge=1, le=30, description="Number of days for trend data"),
):
    """
    Get score trend for a specific goal category.

    Returns trend data points and week-over-week comparison for the specified goal.
    Returns 404 if no data exists for this goal category.
    """
    trend_service = TrendService(db)
    goal_service = GoalService(db)

    # Get trend data
    data_points = await trend_service.get_goal_trend(current_user.id, goal_category, days)

    if not data_points:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No trend data found for goal category: {goal_category}",
        )

    # Get goal description if available
    goals = await goal_service.list(current_user.id)
    goal_description = next(
        (g.description for g in goals if g.category == goal_category),
        None,
    )

    # Calculate week-over-week
    wow = await trend_service.calculate_week_over_week(current_user.id, goal_category)

    return GoalTrendRead(
        goal_category=goal_category,
        goal_description=goal_description,
        data_points=[
            TrendDataPoint(date=dp.date, score=dp.score) for dp in data_points
        ],
        week_over_week=WeekOverWeekComparison(
            this_week_avg=wow.this_week_avg,
            last_week_avg=wow.last_week_avg,
            percentage_change=wow.percentage_change,
            trend=wow.trend,
        ),
    )
