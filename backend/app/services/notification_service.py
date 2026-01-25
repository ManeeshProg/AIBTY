"""Notification service for detecting non-loggers and generating reminders."""
from uuid import UUID
from datetime import date, datetime, time, timedelta
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.journal_entry import JournalEntry
from app.models.daily_score import DailyScore
from app.models.notification import Notification


class NotificationService:
    """
    Service for detecting non-loggers and generating reminder notifications.

    Addresses research pitfall: "Only 12% of notifications arrive at right moment"
    - Respects user preferences (enabled, preferred time)
    - Tracks delivery for fatigue analysis
    - References previous activity for relevance
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_non_loggers(
        self,
        target_date: date,
        cutoff_time: time | None = None,
    ) -> list[User]:
        """
        Find users who haven't logged a journal entry for target_date.

        Args:
            target_date: The date to check for entries
            cutoff_time: Optional - only consider users whose notification_time has passed

        Returns:
            List of User objects with notifications enabled who haven't logged
        """
        # Get all users first (simpler query that works across databases)
        query = select(User)
        result = await self.db.execute(query)
        all_users = list(result.scalars().all())

        # Filter in Python for flexibility
        non_loggers = []
        for user in all_users:
            prefs = user.preferences or {}
            if not prefs.get("notifications_enabled", True):
                continue

            # Check if user logged today
            entry_check = await self.db.execute(
                select(JournalEntry.id).where(
                    and_(
                        JournalEntry.user_id == user.id,
                        JournalEntry.entry_date == target_date,
                    )
                ).limit(1)
            )
            if entry_check.scalar_one_or_none():
                continue  # User has logged

            # Check cutoff time if provided
            if cutoff_time and not self._user_notification_time_passed(user, cutoff_time):
                continue

            non_loggers.append(user)

        return non_loggers

    def _user_notification_time_passed(self, user: User, current_time: time) -> bool:
        """Check if user's preferred notification time has passed."""
        prefs = user.preferences or {}
        notification_time_str = prefs.get("notification_time", "18:00")
        try:
            user_time = datetime.strptime(notification_time_str, "%H:%M").time()
            return current_time >= user_time
        except ValueError:
            return current_time >= time(18, 0)  # Default 6 PM

    async def get_user_activity_summary(
        self,
        user_id: UUID,
        lookback_days: int = 7,
    ) -> dict:
        """
        Get summary of user's recent activity for personalized messaging.

        Returns dict with:
        - last_entry_date: When they last logged
        - days_since_last: How many days ago
        - recent_entry_count: Entries in lookback period
        - yesterday_score: Score from yesterday if exists
        - yesterday_verdict: Verdict from yesterday if exists
        """
        today = date.today()
        lookback_start = today - timedelta(days=lookback_days)

        # Get recent entries
        entries_query = (
            select(JournalEntry)
            .where(
                and_(
                    JournalEntry.user_id == user_id,
                    JournalEntry.entry_date >= lookback_start,
                    JournalEntry.entry_date < today,
                )
            )
            .order_by(JournalEntry.entry_date.desc())
        )
        result = await self.db.execute(entries_query)
        recent_entries = list(result.scalars().all())

        # Get yesterday's score if exists
        yesterday = today - timedelta(days=1)
        score_query = (
            select(DailyScore)
            .where(
                and_(
                    DailyScore.user_id == user_id,
                    DailyScore.score_date == yesterday,
                )
            )
        )
        score_result = await self.db.execute(score_query)
        yesterday_score = score_result.scalar_one_or_none()

        # Calculate summary
        last_entry = recent_entries[0] if recent_entries else None
        days_since = (today - last_entry.entry_date).days if last_entry else None

        return {
            "last_entry_date": last_entry.entry_date if last_entry else None,
            "days_since_last": days_since,
            "recent_entry_count": len(recent_entries),
            "yesterday_score": yesterday_score.composite_score if yesterday_score else None,
            "yesterday_verdict": yesterday_score.verdict if yesterday_score else None,
            "has_recent_activity": len(recent_entries) > 0,
        }

    async def generate_reminder_message(
        self,
        user_id: UUID,
    ) -> str:
        """
        Generate an ego-poking reminder message referencing previous activity.

        Messages use "supportive but with edge" tone per project requirements.
        """
        summary = await self.get_user_activity_summary(user_id)

        # Message templates based on activity
        if summary["days_since_last"] is None:
            return "Your first entry awaits. What happened today that's worth remembering?"

        if summary["days_since_last"] == 1:
            if summary["yesterday_verdict"] == "better":
                return "Yesterday you were better. Today... silence?"
            elif summary["yesterday_score"]:
                return f"Yesterday you scored {int(summary['yesterday_score'])}. Nothing worth mentioning today?"
            else:
                return "Yesterday you showed up. Today's looking quiet."

        if summary["days_since_last"] <= 3:
            return f"It's been {summary['days_since_last']} days. Your streak is watching."

        if summary["days_since_last"] <= 7:
            return f"{summary['days_since_last']} days of silence. The version of you from {summary['recent_entry_count']} entries ago would have something to say about that."

        return "It's been a while. Start small - what's one thing you did today?"

    async def create_notification(
        self,
        user_id: UUID,
        message: str,
        notification_type: str = "reminder",
    ) -> Notification:
        """Create a notification record for a user."""
        notification = Notification(
            user_id=user_id,
            message=message,
            notification_type=notification_type,
        )
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def get_pending_notifications(
        self,
        user_id: UUID,
        limit: int = 10,
    ) -> list[Notification]:
        """Get undelivered notifications for a user (for mobile to fetch)."""
        query = (
            select(Notification)
            .where(
                and_(
                    Notification.user_id == user_id,
                    Notification.delivered_at.is_(None),
                )
            )
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def mark_delivered(self, notification_id: UUID) -> Notification | None:
        """Mark a notification as delivered."""
        query = select(Notification).where(Notification.id == notification_id)
        result = await self.db.execute(query)
        notification = result.scalar_one_or_none()
        if notification:
            notification.delivered_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(notification)
        return notification

    async def mark_read(self, notification_id: UUID) -> Notification | None:
        """Mark a notification as read."""
        query = select(Notification).where(Notification.id == notification_id)
        result = await self.db.execute(query)
        notification = result.scalar_one_or_none()
        if notification:
            notification.read_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(notification)
        return notification

    async def dismiss_notification(self, notification_id: UUID) -> Notification | None:
        """Mark notification as dismissed (for fatigue tracking)."""
        query = select(Notification).where(Notification.id == notification_id)
        result = await self.db.execute(query)
        notification = result.scalar_one_or_none()
        if notification:
            notification.dismissed = True
            await self.db.commit()
            await self.db.refresh(notification)
        return notification
