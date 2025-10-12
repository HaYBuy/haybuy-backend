
from ...database import Base
from sqlalchemy import Boolean, Column, Integer, String,  DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship, mapped_column, Mapped

from datetime import datetime
from zoneinfo import ZoneInfo

from app.schemas.transaction_schema import TransactionStatus

def get_thai_time():
    return datetime.now(ZoneInfo("Asia/Bangkok"))

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    status = Column(String, default=TransactionStatus.PENDING.value)
    agreed_price = Column(DECIMAL(precision=10, scale=2), nullable=False)
    amount = Column(Integer, nullable=False)

    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))
    buyer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    buyer_accept = Column(Boolean, nullable=False, default=False)
    buyer_accept_at = Column(DateTime, nullable=True)

    seller_accept = Column(Boolean, nullable=False, default=False)
    seller_accept_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime(timezone=True), default=get_thai_time)
    updated_at = Column(DateTime(timezone=True), default=get_thai_time, onupdate=get_thai_time)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    paid_at = Column(DateTime(timezone = True), nullable=True)

    item = relationship("Item", back_populates="transaction")
    seller = relationship("User", foreign_keys=[seller_id], back_populates="transactions_sold")
    buyer = relationship("User", foreign_keys=[buyer_id], back_populates="transactions_bought")

