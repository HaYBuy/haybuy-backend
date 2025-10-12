from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ...database import Base


def get_thai_time():
    return datetime.now(ZoneInfo("Asia/Bangkok"))


class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at = Column(DateTime(timezone=True), default=get_thai_time)
    updated_at = Column(
        DateTime(timezone=True), default=get_thai_time, onupdate=get_thai_time
    )

    user = relationship("User", back_populates="carts")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete")
