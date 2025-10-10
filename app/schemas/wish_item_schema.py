
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from typing import List
from enum import Enum

class WishPrivacy(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"


class WishItemBase(BaseModel):
    user_id : int = Field(..., gt=0)
    item_id : int = Field(..., gt=0)
    privacy: str = WishPrivacy.PRIVATE.value

class WishItemCreate(WishItemBase):
    pass

class WishItemResponse(WishItemBase):
    id : int 
    created_at : datetime

    class Config:
        from_attributes = True

    
