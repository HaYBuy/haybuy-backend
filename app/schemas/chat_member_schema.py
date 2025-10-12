from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChatMemberBase(BaseModel):
    chat_id: int
    user_id: int


class ChatMemberCreate(ChatMemberBase):
    pass


class ChatMemberResponse(ChatMemberBase):
    id: int
    createAt: datetime

    model_config = ConfigDict(from_attributes=True)
