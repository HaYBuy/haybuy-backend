from enum import Enum
from pydantic import BaseModel, Field , constr, ConfigDict
from typing import Optional, Pattern, Annotated
from datetime import datetime
from typing import List


class ChatMemberBase(BaseModel):
    chat_id : int
    user_id: int

class ChatMemberCreate(ChatMemberBase):
    pass

class ChatMemberResponse(ChatMemberBase):
    id: int
    createAt: datetime

    model_config = ConfigDict(from_attributes=True)
