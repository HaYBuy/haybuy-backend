from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from typing import List

class GroupRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    owner_id: int = Field(..., gt=0) 

class GroupCreate(GroupBase):
    pass

class GroupResponse(GroupBase):
    id: int
    follower_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
