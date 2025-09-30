from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship, mapped_column, Mapped
from ...database import Base
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo
def get_thai_time():
    return datetime.now(ZoneInfo("Asia/Bangkok"))



class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), default=get_thai_time)
    updated_at = Column(DateTime(timezone=True), default=get_thai_time, onupdate=get_thai_time)
    deleted_at = Column(DateTime(timezone=True), nullable=True) 
    last_login = Column(DateTime(timezone=True), nullable=True)

    items = relationship("Item", back_populates="owner")
    owned_groups = relationship("Group", back_populates="owner")
    groups = relationship("GroupMember", back_populates="user")


    # groups = relationship("Group", secondary="group_members", back_populates="members")
    # transactions = relationship("Transaction", back_populates="user")
    # reviews = relationship("Review", back_populates="user")
    # carts = relationship("Cart", back_populates="user")
    # addresses = relationship("Address", back_populates="user")
    # payments = relationship("Payment", back_populates="user")
    # orders = relationship("Order", back_populates="user")
    # wishlists = relationship("Wishlist", back_populates="user")
    # notifications = relationship("Notification", back_populates="user")
    # messages = relationship("Message", back_populates="user")
 