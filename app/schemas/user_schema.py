from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserBase(BaseModel):
    username: str
    full_name: str
    email: EmailStr
    is_active: bool

class UserCreate(UserBase):
    password_hash: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
    last_login: datetime | None = None

    class Config:
        from_attributes = True