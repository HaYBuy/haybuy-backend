from enum import Enum
from pydantic import BaseModel, Field , constr
from typing import Optional, Pattern, Annotated
from datetime import datetime
from typing import List


class ChatBase(BaseModel):
    pass

class ChatCreate(ChatBase):
    participant_id: int

class ChatResponse(ChatBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True