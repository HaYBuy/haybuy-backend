from enum import Enum
from pydantic import BaseModel, Field , constr
from typing import Optional, Pattern, Annotated
from datetime import datetime
from typing import List

class ChatMessageBase(BaseModel):
    chat_id : int
    sender_id: int
    text: str
    image_url: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageResponse(ChatMessageBase):
    id: int
    sendAt: datetime

    class Config:
        from_attributes = True