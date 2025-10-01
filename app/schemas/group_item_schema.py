from pydantic import BaseModel, Field, condecimal
from datetime import datetime
from typing import Optional
from enum import Enum

class GroupItemStatus(str, Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    SOLD = "sold"
    HIDDEN = "hidden"

class GroupItem(BaseModel):
    pass

class GroupItemCreate(GroupItem):
    group_id : int
    item_id : int

class GroupItemResponse(GroupItem):
    id: int
    group_id : int
    item_id : int
    created_at : datetime

    class Config:
        from_attributes = True