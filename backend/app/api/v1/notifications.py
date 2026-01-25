"""Notification API endpoints."""
from uuid import UUID
from fastapi import APIRouter, HTTPException, status
from app.deps import CurrentUser, DbSession
from app.services.notification_service import NotificationService
from app.schemas.notification import (
    NotificationRead,
    NotificationPreferencesRead,
    NotificationPreferencesUpdate,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationRead])
async def get_pending_notifications(
    db: DbSession,
    current_user: CurrentUser,
    limit: int = 10,
) -> list[NotificationRead]:
    """
    Get pending (undelivered) notifications for current user.

    Mobile app polls this endpoint to fetch notifications for local display.
    """
    service = NotificationService(db)
    notifications = await service.get_pending_notifications(current_user.id, limit)
    return notifications


@router.get("/preferences", response_model=NotificationPreferencesRead)
async def get_notification_preferences(
    current_user: CurrentUser,
) -> NotificationPreferencesRead:
    """
    Get current user's notification preferences.
    """
    prefs = current_user.preferences or {}
    return NotificationPreferencesRead(
        notifications_enabled=prefs.get("notifications_enabled", True),
        notification_time=prefs.get("notification_time", "18:00"),
        timezone=prefs.get("timezone", "UTC"),
    )


@router.patch("/preferences", response_model=NotificationPreferencesRead)
async def update_notification_preferences(
    db: DbSession,
    current_user: CurrentUser,
    update: NotificationPreferencesUpdate,
) -> NotificationPreferencesRead:
    """
    Update current user's notification preferences.

    Allows enabling/disabling notifications and setting preferred notification time.
    """
    prefs = current_user.preferences or {}

    if update.notifications_enabled is not None:
        prefs["notifications_enabled"] = update.notifications_enabled
    if update.notification_time is not None:
        prefs["notification_time"] = update.notification_time
    if update.timezone is not None:
        prefs["timezone"] = update.timezone

    current_user.preferences = prefs
    await db.commit()
    await db.refresh(current_user)

    return NotificationPreferencesRead(
        notifications_enabled=prefs.get("notifications_enabled", True),
        notification_time=prefs.get("notification_time", "18:00"),
        timezone=prefs.get("timezone", "UTC"),
    )


@router.patch("/{notification_id}/delivered", response_model=NotificationRead)
async def mark_notification_delivered(
    db: DbSession,
    current_user: CurrentUser,
    notification_id: UUID,
) -> NotificationRead:
    """
    Mark a notification as delivered.

    Called by mobile when notification is shown to user.
    """
    service = NotificationService(db)
    notification = await service.mark_delivered(notification_id)

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this notification",
        )

    return notification


@router.patch("/{notification_id}/read", response_model=NotificationRead)
async def mark_notification_read(
    db: DbSession,
    current_user: CurrentUser,
    notification_id: UUID,
) -> NotificationRead:
    """
    Mark a notification as read.

    Called by mobile when user interacts with notification.
    """
    service = NotificationService(db)
    notification = await service.mark_read(notification_id)

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this notification",
        )

    return notification


@router.patch("/{notification_id}/dismiss", response_model=NotificationRead)
async def dismiss_notification(
    db: DbSession,
    current_user: CurrentUser,
    notification_id: UUID,
) -> NotificationRead:
    """
    Dismiss a notification without reading.

    Used for fatigue tracking - dismissals indicate notification wasn't valuable.
    """
    service = NotificationService(db)
    notification = await service.dismiss_notification(notification_id)

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this notification",
        )

    return notification
