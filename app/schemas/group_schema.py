"""Group schema definitions."""

from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from typing import List


class GroupRole(str, Enum):
    """Enumeration of possible group member roles."""

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class GroupBase(BaseModel):
    """Base group model with common fields."""

    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None


class GroupCreate(GroupBase):
    """Schema for creating a new group."""

    owner_id: int = Field(..., gt=0)


class GroupResponse(GroupBase):
    id: int
    owner_id: int = Field(..., gt=0)
    follower_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
