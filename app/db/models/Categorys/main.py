
from datetime import datetime
from zoneinfo import ZoneInfo
from ...database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped, backref
from ....schemas.category_schema import CategoryBase
from typing import List, Optional


def get_thai_time():
    return datetime.now(ZoneInfo("Asia/Bangkok"))

class Category(Base):
    __tablename__ = "categories"

    id : Mapped[int] = mapped_column(primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    slug = Column(String, nullable=False)

    parent_id : Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"), nullable=True)

    parent : Mapped[Optional["Category"]] = relationship(
        "Category",
        remote_side=[id],  # บอก SQLAlchemy ว่า parent_id อ้างอิงกับ id ของตารางเดียวกัน
        backref=backref("children", cascade="all, delete")
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_thai_time)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_thai_time, onupdate=get_thai_time)


