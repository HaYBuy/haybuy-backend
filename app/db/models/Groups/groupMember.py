from ...database import Base
from sqlalchemy import Column,  ForeignKey , String, DateTime
from sqlalchemy.orm import relationship, mapped_column, Mapped

from datetime import datetime
from zoneinfo import ZoneInfo

def get_thai_time():
    return datetime.now(ZoneInfo("Asia/Bangkok"))

class GroupMember(Base):
    __tablename__ = "group_members"

    id : Mapped[int] = mapped_column(primary_key=True, index=True)
    group_id : Mapped[int] = mapped_column(ForeignKey("groups.id"))
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"))
    role = Column(String, default="admin")  # e.g., 'admin', 'member'

    created_at = Column(DateTime(timezone=True), default=get_thai_time)
    updated_at = Column(DateTime(timezone=True), default=get_thai_time, onupdate=get_thai_time)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    group = relationship("Group", back_populates="members")
    user = relationship("User", back_populates="groups")
