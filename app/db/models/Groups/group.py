
from datetime import datetime
from zoneinfo import ZoneInfo
from ...database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from ....schemas.group_schema import GroupBase
from typing import List, Optional


def get_thai_time():
    return datetime.now(ZoneInfo("Asia/Bangkok"))

class Group(Base):
    __tablename__ = "groups"

    id : Mapped[int] = mapped_column(primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    follower_count = Column(Integer, default=0)
    
    owner_id : Mapped[int] = mapped_column(ForeignKey("users.id"))
    # member_ids : Mapped[int] = Column(String, nullable=True)  # Comma-separated user IDs

    owner = relationship("User", back_populates="owned_groups")
    items = relationship("GroupItem", back_populates="group")
    members = relationship("GroupMember", back_populates="group")

    created_at = Column(DateTime(timezone=True), default=get_thai_time)
    updated_at = Column(DateTime(timezone=True), default=get_thai_time, onupdate=get_thai_time)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

