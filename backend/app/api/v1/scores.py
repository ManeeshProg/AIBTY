"""Scoring API endpoints."""

from datetime import date, datetime
from fastapi import APIRouter, HTTPException, status, Query

from app.deps import DbSession, CurrentUser
from app.schemas.score import (
    ScoreRequest,
    ScoringResponse,
    DailyScoreRead,
    StreakResponse,
)
from app.services.scoring_service import ScoringService

router = APIRouter(prefix="/scores", tags=["scores"])


@router.post("/score", response_model=ScoringResponse)
async def trigger_scoring(
    request: ScoreRequest,
    db: DbSession,
    current_user: CurrentUser,
):
    """
    Trigger scoring for a specific date.

    Runs complete scoring pipeline:
    - Deterministic scoring
    - LLM enhancement
    - Comparison with yesterday
    - Streak tracking
    - Persistence

    Args:
        request: ScoreRequest with score_date
        db: Database session
        current_user: Authenticated user

    Returns:
        ScoringResponse with verdict, scores, and streaks

    Raises:
        404: If no journal entry exists for the date
        404: If no active goals exist
    """
    service = ScoringService(db)

    try:
        result = await service.score_day(
            user_id=current_user.id,
            score_date=request.score_date,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/today", response_model=DailyScoreRead)
async def get_today_score(
    db: DbSession,
    current_user: CurrentUser,
):
    """Get today's score if it exists."""
    from sqlalchemy import select
    from app.models.daily_score import DailyScore
    from sqlalchemy.orm import selectinload

    today = date.today()
    result = await db.execute(
        select(DailyScore)
        .options(selectinload(DailyScore.metrics))
        .where(
            DailyScore.user_id == current_user.id,
            DailyScore.score_date == today,
        )
    )
    score = result.scalar_one_or_none()

    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No score found for today",
        )

    return score


@router.get("/{score_date}", response_model=DailyScoreRead)
async def get_score_by_date(
    score_date: date,
    db: DbSession,
    current_user: CurrentUser,
):
    """Get score for a specific date."""
    from sqlalchemy import select
    from app.models.daily_score import DailyScore
    from sqlalchemy.orm import selectinload

    result = await db.execute(
        select(DailyScore)
        .options(selectinload(DailyScore.metrics))
        .where(
            DailyScore.user_id == current_user.id,
            DailyScore.score_date == score_date,
        )
    )
    score = result.scalar_one_or_none()

    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No score found for {score_date}",
        )

    return score


@router.get("/streaks/all", response_model=StreakResponse)
async def get_all_streaks(
    db: DbSession,
    current_user: CurrentUser,
):
    """Get streak information for all goals."""
    service = ScoringService(db)
    streaks = await service.get_streaks(current_user.id)
    return StreakResponse(streaks=streaks)


@router.get("/history", response_model=list[DailyScoreRead])
async def get_score_history(
    db: DbSession,
    current_user: CurrentUser,
    from_date: date | None = Query(None, description="Start date for history"),
    to_date: date | None = Query(None, description="End date for history"),
    limit: int = Query(30, ge=1, le=365, description="Maximum number of scores to return"),
):
    """
    Get score history with optional date filtering.

    Args:
        from_date: Start date (inclusive)
        to_date: End date (inclusive)
        limit: Maximum number of scores (default 30, max 365)

    Returns:
        List of DailyScoreRead ordered by date descending
    """
    from sqlalchemy import select
    from app.models.daily_score import DailyScore
    from sqlalchemy.orm import selectinload

    query = (
        select(DailyScore)
        .options(selectinload(DailyScore.metrics))
        .where(DailyScore.user_id == current_user.id)
        .order_by(DailyScore.score_date.desc())
        .limit(limit)
    )

    if from_date:
        query = query.where(DailyScore.score_date >= from_date)
    if to_date:
        query = query.where(DailyScore.score_date <= to_date)

    result = await db.execute(query)
    scores = list(result.scalars().all())

    return scores
