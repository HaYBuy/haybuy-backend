from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class GroupMemberRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"

class GroupMemberBase(BaseModel):
    user_id: int = Field(..., gt=0)
    group_id: int = Field(..., gt=0)
    role: GroupMemberRole = GroupMemberRole.ADMIN
class GroupMemberCreate(GroupMemberBase):
    pass

class GroupMemberResponse(GroupMemberBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True