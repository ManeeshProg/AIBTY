"""Celery tasks for notification scheduling."""
import asyncio
import logging
from datetime import date, datetime
from uuid import UUID

from sqlalchemy import select, and_, func

from app.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.services.notification_service import NotificationService
from app.models.notification import Notification

logger = logging.getLogger(__name__)


def run_async(coro):
    """Helper to run async code in sync Celery task."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(
    name="app.tasks.notification_tasks.check_and_notify_non_loggers",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def check_and_notify_non_loggers(self):
    """
    Check for users who haven't logged today and create reminder notifications.

    This task runs hourly and:
    1. Finds users whose notification time has passed
    2. Checks if they've logged today
    3. Generates and stores reminder notifications for non-loggers

    The notification is stored in DB; mobile fetches and delivers via push.
    """
    logger.info("Starting non-logger notification check")

    try:
        result = run_async(_check_and_notify())
        logger.info(f"Notification check complete: {result}")
        return result
    except Exception as exc:
        logger.error(f"Notification check failed: {exc}")
        raise self.retry(exc=exc)


async def _check_and_notify() -> dict:
    """Async implementation of notification check."""
    async with AsyncSessionLocal() as db:
        service = NotificationService(db)

        today = date.today()
        current_time = datetime.now().time()

        # Get non-loggers whose notification time has passed
        non_loggers = await service.get_non_loggers(
            target_date=today,
            cutoff_time=current_time,
        )

        notifications_created = 0
        for user in non_loggers:
            # Check if we already sent a notification today
            existing = await _has_notification_today(db, user.id, today)
            if existing:
                continue

            # Generate personalized message
            message = await service.generate_reminder_message(user.id)

            # Create notification record
            await service.create_notification(
                user_id=user.id,
                message=message,
                notification_type="reminder",
            )
            notifications_created += 1
            logger.info(f"Created notification for user {user.id}")

        return {
            "checked_users": len(non_loggers),
            "notifications_created": notifications_created,
            "timestamp": datetime.utcnow().isoformat(),
        }


async def _has_notification_today(db, user_id: UUID, target_date: date) -> bool:
    """Check if user already received a reminder notification today."""
    query = select(Notification).where(
        and_(
            Notification.user_id == user_id,
            Notification.notification_type == "reminder",
            func.date(Notification.created_at) == target_date,
        )
    )
    result = await db.execute(query)
    return result.scalar_one_or_none() is not None


@celery_app.task(
    name="app.tasks.notification_tasks.send_notification_to_user",
    bind=True,
    max_retries=3,
)
def send_notification_to_user(self, user_id: str, message: str):
    """
    Create a notification for a specific user.

    Can be called directly to send ad-hoc notifications.
    """
    logger.info(f"Creating notification for user {user_id}")

    try:
        result = run_async(_create_user_notification(user_id, message))
        return result
    except Exception as exc:
        logger.error(f"Failed to create notification: {exc}")
        raise self.retry(exc=exc)


async def _create_user_notification(user_id: str, message: str) -> dict:
    """Async implementation of single user notification."""
    async with AsyncSessionLocal() as db:
        service = NotificationService(db)
        notification = await service.create_notification(
            user_id=UUID(user_id),
            message=message,
            notification_type="reminder",
        )
        return {
            "notification_id": str(notification.id),
            "user_id": user_id,
            "created": True,
        }
