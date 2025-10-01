from pydantic import BaseModel, Field, condecimal
from datetime import datetime
from typing import Optional
from enum import Enum

class TransactionStatus(str, Enum):
    PENDING = "pending"
    CANCELLED = "cancelled"
    ACCEPTED = "accepted"


class TransactionBase(BaseModel):
    item_id : int = Field(..., gt=0)
    seller_id : int = Field(..., gt=0)
    buyer_id : int = Field(..., gt=0)
    amount : int

class TransactionCreate(TransactionBase):
    agreed_price : condecimal(max_digits=10, decimal_places=2)

class TransactionAccepted(BaseModel):
    accepter : bool
    accept_at : datetime


class TransactionResponse(TransactionBase):
    id: int
    agreed_price : condecimal(max_digits=10, decimal_places=2)
    status: TransactionStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    buyer_accept : bool
    seller_accept : bool
    buyer_accept_at : Optional[datetime]
    seller_accept_at : Optional[datetime]

    class Config:
        from_attributes = True
