from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional
from .cart_item_response import CartItemResponse


class CartBase(BaseModel):
    pass

class CartCreate(CartBase):
    pass


class CartResponse(CartBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    items: List[CartItemResponse] = []

    model_config = ConfigDict(from_attributes=True)
