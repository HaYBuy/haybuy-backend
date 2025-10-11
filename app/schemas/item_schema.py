"""Item schema definitions."""

from pydantic import BaseModel, Field, condecimal
from decimal import Decimal
from datetime import datetime
from typing import Optional
from enum import Enum


class ItemStatus(str, Enum):
    """Enumeration of possible item statuses."""

    AVAILABLE = "available"
    RESERVED = "reserved"
    SOLD = "sold"
    HIDDEN = "hidden"


class ItemBase(BaseModel):
    """Base item model with common fields."""

    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    price: Decimal = Field(
        ..., ge=0, max_digits=10, decimal_places=2
    )  # ge=0 means greater than or equal to 0
    quantity: int = Field(..., ge=0)  # quantity must be >= 0
    status: ItemStatus = ItemStatus.AVAILABLE
    image_url: Optional[str] = None
    search_text: Optional[str] = None
    category_id: int = Field(..., gt=0)


class ItemCreate(ItemBase):
    """Schema for creating a new item."""


class ItemStatusUpdate(BaseModel):
    """Schema for updating item status only."""

    status: ItemStatus


class ItemResponse(ItemBase):
    id: int
    owner_id: int = Field(..., gt=0)
    group_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
