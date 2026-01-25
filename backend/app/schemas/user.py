from uuid import UUID
from datetime import datetime, time
from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: str | None = None
    preferences: dict | None = None


class UserRead(UserBase):
    id: UUID
    preferences: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserPreferencesUpdate(BaseModel):
    """Schema for updating user scheduling preferences."""
    analysis_time: time | None = None  # 24h format, e.g., 21:00
    timezone: str | None = None  # IANA timezone, e.g., "America/New_York"


class UserPreferencesRead(BaseModel):
    """Schema for reading user scheduling preferences."""
    analysis_time: time | None
    timezone: str

    model_config = ConfigDict(from_attributes=True)
