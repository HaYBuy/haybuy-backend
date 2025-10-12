from datetime import datetime
from enum import Enum
from typing import Annotated, List, Optional, Pattern

from pydantic import BaseModel, ConfigDict


class ChatMessageBase(BaseModel):
    chat_id: int
    text: Optional[str]
    image_url: Optional[str]


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessageResponse(ChatMessageBase):
    id: int
    send_at: datetime

    model_config = ConfigDict(from_attributes=True)
