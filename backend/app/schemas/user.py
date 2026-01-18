from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr


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
