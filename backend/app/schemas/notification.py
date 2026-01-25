"""Notification API schemas."""
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class NotificationRead(BaseModel):
    """Schema for reading a notification."""
    id: UUID
    message: str
    notification_type: str
    created_at: datetime
    delivered_at: datetime | None
    read_at: datetime | None
    dismissed: bool

    model_config = ConfigDict(from_attributes=True)


class NotificationPreferencesRead(BaseModel):
    """Schema for reading notification preferences.

    These preferences are stored in the User.preferences JSON field.
    """
    notifications_enabled: bool = True
    notification_time: str = "18:00"  # 24h format
    timezone: str = "UTC"


class NotificationPreferencesUpdate(BaseModel):
    """Schema for updating notification preferences.

    Updates the notification-related fields in User.preferences JSON.
    """
    notifications_enabled: bool | None = None
    notification_time: str | None = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    timezone: str | None = None
