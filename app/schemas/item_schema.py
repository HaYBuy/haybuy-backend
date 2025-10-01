from pydantic import BaseModel, Field, condecimal
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
    price: condecimal(max_digits=10, decimal_places=2)
    quantity: int
    status: ItemStatus = ItemStatus.AVAILABLE
    image_url: Optional[str] = None
    search_text : Optional[str] = None
    category_id: int = Field(..., gt=0 )
    group_id: Optional[int] = None

class ItemCreate(ItemBase):
    pass

class ItemResponse(ItemBase):
    id: int
    owner_id: int = Field(..., gt=0)
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True