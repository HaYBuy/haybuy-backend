from ...database import Base
from sqlalchemy import Column, Integer, String, Float , DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship, mapped_column, Mapped

from datetime import datetime
from zoneinfo import ZoneInfo

def get_thai_time():
    return datetime.now(ZoneInfo("Asia/Bangkok"))

class PriceHistory(Base):
    __tablename__ = "priceHistorys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    price = Column(DECIMAL(precision=10, scale=2), nullable=False)

    item_id : Mapped[int] = mapped_column(ForeignKey("items.id"))
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"))

    item = relationship("Item", back_populates="priceHistory")
    user = relationship("User", back_populates="editPrice")


