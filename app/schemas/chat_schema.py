from enum import Enum
from pydantic import BaseModel, Field , constr
from typing import Optional, Pattern, Annotated
from datetime import datetime
from typing import List


class ChatBase(BaseModel):
    pass

class ChatCreate(ChatBase):
    pass

class ChatResponse(ChatBase):
    id: int
    createAt: datetime
    updateAt: datetime

    class Config:
        from_attributes = True