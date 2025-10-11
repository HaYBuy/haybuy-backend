"""Price history schema definitions."""
from pydantic import BaseModel, Field, condecimal
from datetime import datetime
from typing import Optional


class PriceHistoryBase(BaseModel):
    """Base price history model with common fields."""
    item_id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)
    price: condecimal(max_digits=10, decimal_places=2)

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }


class PriceHistoryCreate(PriceHistoryBase):
    """Schema for creating a new price history entry."""

class PriceHistoryResponse(PriceHistoryBase):
    id : int
    start_date: datetime
    end_date: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }
        