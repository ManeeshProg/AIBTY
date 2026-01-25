"""Celery tasks for evening analysis orchestration."""
import logging
from datetime import date, datetime, timezone
from uuid import UUID

from app.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.services.analysis_orchestrator import AnalysisOrchestrator

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.orchestrator.check_due_analyses")
def check_due_analyses():
    """
    Periodic task that runs every minute via Celery beat.

    Finds users due for analysis and spawns individual analysis tasks.
    """
    import asyncio

    async def _check():
        async with AsyncSessionLocal() as db:
            orchestrator = AnalysisOrchestrator(db)
            due_users = await orchestrator.get_users_due_for_analysis()

            logger.info(f"Found {len(due_users)} users due for analysis")

            for user in due_users:
                # Determine analysis date (today in user's timezone)
                from zoneinfo import ZoneInfo
                user_tz = ZoneInfo(user.timezone or "UTC")
                user_now = datetime.now(timezone.utc).astimezone(user_tz)
                analysis_date = user_now.date()

                # Spawn individual analysis task
                run_user_analysis.delay(str(user.id), analysis_date.isoformat())
                logger.info(
                    f"Spawned analysis task for user {user.id} "
                    f"for date {analysis_date}"
                )

    asyncio.run(_check())


@celery_app.task(
    name="app.tasks.orchestrator.run_user_analysis",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=3600,
    retry_jitter=True,
    max_retries=3,
)
def run_user_analysis(self, user_id: str, analysis_date_str: str):
    """
    Run analysis for a specific user and date.

    Uses exponential backoff on failure.
    """
    import asyncio

    analysis_date = date.fromisoformat(analysis_date_str)
    user_uuid = UUID(user_id)

    logger.info(
        f"Running analysis for user {user_id} on {analysis_date}, "
        f"attempt {self.request.retries + 1}"
    )

    async def _run():
        async with AsyncSessionLocal() as db:
            orchestrator = AnalysisOrchestrator(db)
            result = await orchestrator.run_analysis(
                user_uuid,
                analysis_date,
                celery_task_id=self.request.id,
            )
            return result

    try:
        result = asyncio.run(_run())
        if result:
            logger.info(
                f"Analysis completed for user {user_id}: "
                f"verdict={result.verdict}, score={result.composite_score}"
            )
        else:
            logger.info(f"No entries to analyze for user {user_id}")
        return {"status": "completed", "user_id": user_id, "date": analysis_date_str}

    except Exception as e:
        logger.error(
            f"Analysis failed for user {user_id} on attempt "
            f"{self.request.retries + 1}: {e}"
        )
        raise


@celery_app.task(name="app.tasks.orchestrator.run_manual_analysis")
def run_manual_analysis(user_id: str, analysis_date_str: str | None = None):
    """
    Manually trigger analysis for a user (e.g., from API endpoint).
    """
    import asyncio

    if analysis_date_str:
        analysis_date = date.fromisoformat(analysis_date_str)
    else:
        analysis_date = date.today()

    user_uuid = UUID(user_id)

    logger.info(f"Manual analysis triggered for user {user_id} on {analysis_date}")

    async def _run():
        async with AsyncSessionLocal() as db:
            orchestrator = AnalysisOrchestrator(db)
            return await orchestrator.run_analysis(user_uuid, analysis_date)

    result = asyncio.run(_run())
    return {
        "status": "completed" if result else "no_entries",
        "user_id": user_id,
        "date": analysis_date.isoformat(),
    }
