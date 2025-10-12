from ...database import Base
from sqlalchemy import Column, ForeignKey , DateTime
from sqlalchemy.orm import relationship, mapped_column, Mapped
from datetime import datetime
from zoneinfo import ZoneInfo

def get_thai_time():
    return datetime.now(ZoneInfo("Asia/Bangkok"))

class GroupItem(Base):
    __tablename__ = "group_items"
    id : Mapped[int] = mapped_column(primary_key=True, index=True)
    group_id : Mapped[int] = mapped_column(ForeignKey("groups.id"))
    item_id : Mapped[int] = mapped_column(ForeignKey("items.id"))

    created_at = Column(DateTime(timezone=True), default=get_thai_time)

    group = relationship("Group", back_populates="items")
    item = relationship("Item", back_populates="group")
