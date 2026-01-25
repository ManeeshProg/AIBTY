"""Notification service for managing user notifications.

Minimal implementation for API endpoints. Full implementation in 07-02.
"""
from uuid import UUID
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from app.models.notification import Notification


class NotificationService:
    """Service for managing notifications."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_pending_notifications(
        self, user_id: UUID, limit: int = 10
    ) -> list[Notification]:
        """Get pending (undelivered) notifications for a user.

        Args:
            user_id: The user's ID
            limit: Maximum number of notifications to return

        Returns:
            List of pending notifications, ordered by creation time (newest first)
        """
        result = await self.db.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .where(Notification.delivered_at.is_(None))
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def mark_delivered(self, notification_id: UUID) -> Notification | None:
        """Mark a notification as delivered.

        Args:
            notification_id: The notification's ID

        Returns:
            The updated notification, or None if not found
        """
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()

        if notification:
            notification.delivered_at = datetime.now()
            await self.db.commit()
            await self.db.refresh(notification)

        return notification

    async def mark_read(self, notification_id: UUID) -> Notification | None:
        """Mark a notification as read.

        Args:
            notification_id: The notification's ID

        Returns:
            The updated notification, or None if not found
        """
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()

        if notification:
            notification.read_at = datetime.now()
            await self.db.commit()
            await self.db.refresh(notification)

        return notification

    async def dismiss_notification(self, notification_id: UUID) -> Notification | None:
        """Dismiss a notification without reading.

        Used for fatigue tracking - dismissals indicate the notification
        wasn't valuable to the user.

        Args:
            notification_id: The notification's ID

        Returns:
            The updated notification, or None if not found
        """
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()

        if notification:
            notification.dismissed = True
            await self.db.commit()
            await self.db.refresh(notification)

        return notification
