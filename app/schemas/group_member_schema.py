"""Group member schema definitions."""

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class GroupMemberRole(str, Enum):
    """Enumeration of possible group member roles."""

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class GroupMemberBase(BaseModel):
    """Base group member model with common fields."""

    user_id: int = Field(..., gt=0)
    group_id: int = Field(..., gt=0)
    role: GroupMemberRole = GroupMemberRole.ADMIN


class GroupMemberCreate(GroupMemberBase):
    """Schema for creating a new group member."""


class GroupMemberResponse(GroupMemberBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
