from datetime import datetime
from enum import Enum
from typing import Annotated, List, Optional, Pattern

from pydantic import BaseModel, ConfigDict


class ChatBase(BaseModel):
    pass


class ChatCreate(ChatBase):
    participant_id: int


class ChatResponse(ChatBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
