from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserBase(BaseModel):
    username: str = Field(..., min_length=1, description="Username must not be empty")
    full_name: str = Field(..., min_length=1, description="Full name must not be empty")
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=1, description="Password must not be empty")


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
    last_login: datetime | None = None

    class Config:
        from_attributes = True
