"""Analysis orchestrator service for evening analysis pipeline."""
import logging
from datetime import date, datetime, timezone as tz
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.journal_entry import JournalEntry
from app.models.daily_score import DailyScore
from app.models.analysis_run import AnalysisRun

logger = logging.getLogger(__name__)


class AnalysisOrchestrator:
    """
    Coordinates the evening analysis pipeline.

    Responsibilities:
    - Find users due for analysis at current time
    - Aggregate day's journal entries
    - Orchestrate extraction -> scoring -> verdict pipeline
    - Track analysis runs for idempotency
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_users_due_for_analysis(self) -> list[User]:
        """
        Find users whose analysis_time matches current time (within the minute).

        Checks each user's timezone to determine if it's their scheduled time.
        """
        now_utc = datetime.now(tz.utc)

        # Get all users with analysis_time set
        result = await self.db.execute(
            select(User).where(User.analysis_time.isnot(None))
        )
        users = list(result.scalars().all())

        due_users = []
        for user in users:
            try:
                user_tz = ZoneInfo(user.timezone or "UTC")
                user_now = now_utc.astimezone(user_tz)
                user_time = user_now.time()

                # Check if current time matches analysis_time (same hour and minute)
                if (user_time.hour == user.analysis_time.hour and
                    user_time.minute == user.analysis_time.minute):
                    # Check if we already ran analysis today for this user
                    today_in_user_tz = user_now.date()
                    existing = await self._get_analysis_run(user.id, today_in_user_tz)
                    if not existing or existing.status == "failed":
                        due_users.append(user)
            except Exception as e:
                logger.warning(f"Error checking user {user.id} for analysis: {e}")
                continue

        return due_users

    async def _get_analysis_run(
        self, user_id: UUID, analysis_date: date
    ) -> AnalysisRun | None:
        """Get existing analysis run for user and date."""
        result = await self.db.execute(
            select(AnalysisRun).where(
                and_(
                    AnalysisRun.user_id == user_id,
                    AnalysisRun.analysis_date == analysis_date,
                )
            )
        )
        return result.scalar_one_or_none()

    async def create_or_get_analysis_run(
        self, user_id: UUID, analysis_date: date, celery_task_id: str | None = None
    ) -> AnalysisRun:
        """Create new analysis run or return existing one."""
        existing = await self._get_analysis_run(user_id, analysis_date)
        if existing:
            return existing

        run = AnalysisRun(
            user_id=user_id,
            analysis_date=analysis_date,
            status="pending",
            celery_task_id=celery_task_id,
        )
        self.db.add(run)
        await self.db.commit()
        await self.db.refresh(run)
        return run

    async def get_day_entries(
        self, user_id: UUID, entry_date: date
    ) -> list[JournalEntry]:
        """Get all journal entries for a user on a specific date."""
        result = await self.db.execute(
            select(JournalEntry)
            .options(selectinload(JournalEntry.metrics))
            .where(
                and_(
                    JournalEntry.user_id == user_id,
                    JournalEntry.entry_date == entry_date,
                )
            )
            .order_by(JournalEntry.created_at)
        )
        return list(result.scalars().all())

    async def aggregate_day_content(self, entries: list[JournalEntry]) -> str:
        """
        Aggregate all entries into single content block for analysis.

        Preserves chronological order and source information.
        """
        if not entries:
            return ""

        parts = []
        for entry in entries:
            timestamp = entry.created_at.strftime("%H:%M") if entry.created_at else "unknown"
            source = f"[{entry.input_source}, {timestamp}]"
            parts.append(f"{source}\n{entry.content_markdown}")

        return "\n\n---\n\n".join(parts)

    async def run_analysis(
        self, user_id: UUID, analysis_date: date, celery_task_id: str | None = None
    ) -> DailyScore | None:
        """
        Run the full analysis pipeline for a user's day.

        Pipeline:
        1. Get/create AnalysisRun record
        2. Aggregate day's journal entries
        3. Run extraction (Phase 3)
        4. Run scoring (Phase 2)
        5. Generate verdict (Phase 5)
        6. Update AnalysisRun status

        Returns DailyScore on success, None on failure.
        """
        run = await self.create_or_get_analysis_run(
            user_id, analysis_date, celery_task_id
        )

        # Mark as running
        run.status = "running"
        run.started_at = datetime.now(tz.utc)
        await self.db.commit()

        try:
            # Step 1: Get day's entries
            entries = await self.get_day_entries(user_id, analysis_date)
            run.entries_processed = len(entries)

            if not entries:
                logger.info(f"No entries for user {user_id} on {analysis_date}")
                run.status = "completed"
                run.completed_at = datetime.now(tz.utc)
                await self.db.commit()
                return None

            # Step 2: Aggregate content
            aggregated_content = await self.aggregate_day_content(entries)
            logger.info(
                f"Aggregated {len(entries)} entries for user {user_id}, "
                f"total length: {len(aggregated_content)}"
            )

            # Step 3-5: Run extraction, scoring, verdict
            # These services are already implemented in Phases 2, 3, 5
            # Integration will be done when connecting the full pipeline
            # For now, mark as completed with placeholder data

            # Mark run as completed
            run.status = "completed"
            run.completed_at = datetime.now(tz.utc)
            await self.db.commit()

            logger.info(
                f"Analysis completed for user {user_id} on {analysis_date}: "
                f"{len(entries)} entries processed"
            )
            return None  # Return None until full pipeline integration

        except Exception as e:
            logger.error(f"Analysis failed for user {user_id}: {e}")
            run.status = "failed"
            run.error_message = str(e)
            run.retry_count += 1
            await self.db.commit()
            raise
