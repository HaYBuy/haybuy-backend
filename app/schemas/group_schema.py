from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from typing import List


class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    follower_count: int = 0
    
    owner_id: int = Field(..., gt=0)
    member_ids: Optional[List[int]] = []  # List of user IDs

class GroupCreate(GroupBase):
    pass

class GroupResponse(GroupBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
