from ...database import Base
from sqlalchemy import Column, Integer, String, Float , DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship, mapped_column, Mapped

from datetime import datetime
from zoneinfo import ZoneInfo

def get_thai_time():
    return datetime.now(ZoneInfo("Asia/Bangkok"))

class WishItem(Base):
    __tablename__ = "wishItems"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id : Mapped[int] = mapped_column(Integer, nullable=False)
    item_id : Mapped[int] = mapped_column(Integer, nullable=False)
    privacy = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_thai_time)

    wisher = relationship("User", back_populates="wishItem")
    itemWish = relationship("Item", back_populates="wishItem")


    


