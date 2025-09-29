from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class ItemStatus(str, Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    SOLD = "sold"
    HIDDEN = "hidden"

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    quantity: int
    status: ItemStatus = ItemStatus.AVAILABLE
    image_url: Optional[str] = None
    search_text : Optional[str] = None

    owner_id: int = Field(..., gt=0)
    category_id: int = Field(..., gt=0 )
    group_id: Optional[int] = None

class ItemCreate(ItemBase):
    pass

class ItemResponse(ItemBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True