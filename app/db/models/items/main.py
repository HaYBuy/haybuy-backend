from ...database import Base
from sqlalchemy import Column, Integer, String, Float , DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship, mapped_column, Mapped

from datetime import datetime
from zoneinfo import ZoneInfo



from ....schemas.item_schema import ItemStatus

def get_thai_time():
    return datetime.now(ZoneInfo("Asia/Bangkok"))


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    price = Column(DECIMAL(precision=10, scale=2), nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(String, default=ItemStatus.AVAILABLE.value)
    image_url = Column(String, nullable=True)
    search_text = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), default=get_thai_time)
    updated_at = Column(DateTime(timezone=True), default=get_thai_time, onupdate=get_thai_time)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    category_id: Mapped[int] = mapped_column(Integer, nullable=False)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"))

    owner = relationship("User", back_populates="items")  
    group = relationship("Group", back_populates="items")
    priceHistory = relationship("PriceHistory", back_populates="item")

