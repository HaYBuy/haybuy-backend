from enum import Enum
from pydantic import BaseModel, Field , constr, ConfigDict
from typing import Optional, Pattern, Annotated
from datetime import datetime
from typing import List

class ChatMessageBase(BaseModel):
    chat_id : int
    text: Optional[str]
    image_url: Optional[str]

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageResponse(ChatMessageBase):
    id: int
    send_at: datetime

    model_config = ConfigDict(from_attributes=True)