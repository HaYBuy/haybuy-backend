from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)
