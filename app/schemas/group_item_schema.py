"""Group item schema definitions."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class GroupItemStatus(str, Enum):
    """Enumeration of possible group item statuses."""

    AVAILABLE = "available"
    RESERVED = "reserved"
    SOLD = "sold"
    HIDDEN = "hidden"


class GroupItem(BaseModel):
    """Base group item model."""


class GroupItemCreate(GroupItem):
    """Schema for creating a new group item."""

    group_id: int = Field(..., gt=0)
    item_id: int = Field(..., gt=0)


class GroupItemResponse(GroupItem):
    id: int
    group_id: int
    item_id: int
    created_at: datetime

    class Config:
        from_attributes = True
