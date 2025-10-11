from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class CartItemBase(BaseModel):
    product_id: int
    quantity: int


class CartItemCreate(CartItemBase):
    pass


class CartItemResponse(CartItemBase):
    id: int
    price: float

    class Config:
        from_attributes = True