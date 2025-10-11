from ...database import Base
from sqlalchemy import Column, Integer, ForeignKey , String, DateTime
from sqlalchemy.orm import relationship, mapped_column, Mapped
from ....schemas.group_member_schema import GroupMemberBase
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional


def get_thai_time():
    return datetime.now(ZoneInfo("Asia/Bangkok"))

class ChatMember(Base):
    __tablename__ = "chat_members"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_thai_time)

    # ความสัมพันธ์
    chat = relationship("Chat", back_populates="members")
    user = relationship("User", back_populates="chat_members") 