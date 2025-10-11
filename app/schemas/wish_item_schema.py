"""Wish item schema definitions."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from typing import List
from enum import Enum


class WishPrivacy(str, Enum):
    """Enumeration of wish item privacy settings."""
    PUBLIC = "public"
    PRIVATE = "private"


class WishItemBase(BaseModel):
    """Base wish item model with common fields."""
    user_id: int = Field(..., gt=0)
    item_id: int = Field(..., gt=0)
    privacy: str = WishPrivacy.PRIVATE.value


class WishItemCreate(WishItemBase):
    """Schema for creating a new wish item."""

class WishItemResponse(WishItemBase):
    id : int 
    created_at : datetime

    class Config:
        from_attributes = True

    
