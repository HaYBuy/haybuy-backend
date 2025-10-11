from ...database import Base
from sqlalchemy import Column, Integer, ForeignKey , String, DateTime
from sqlalchemy.orm import relationship, mapped_column, Mapped
from ....schemas.group_member_schema import GroupMemberBase
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional

def get_thai_time():
    return datetime.now(ZoneInfo("Asia/Bangkok"))

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=get_thai_time)
    updated_at = Column(DateTime(timezone=True), default=get_thai_time, onupdate=get_thai_time)

    messages = relationship("ChatMessage", back_populates="chat", cascade="all, delete-orphan")
    members = relationship("ChatMember", back_populates="chat", cascade="all, delete-orphan")