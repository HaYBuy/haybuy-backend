from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship, mapped_column, Mapped
from ...database import Base
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo


from ..Chats.chat_message import ChatMessage 
from ..Chats.chat_member import ChatMember 
from ..Chats.chat import Chat

def get_thai_time():
    return datetime.now(ZoneInfo("Asia/Bangkok"))



class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
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
    editPrice = relationship("PriceHistory", back_populates="editer")
    wishItem = relationship("WishItem", back_populates="wisher")
    profile = relationship("UserProfile", back_populates="user")

    send_messages = relationship("ChatMessage", back_populates="sender")
    chat_members = relationship("ChatMember", back_populates="user")

    carts = relationship("Cart", back_populates="user")


    transactions_sold = relationship("Transaction", foreign_keys="[Transaction.seller_id]", back_populates="seller")
    transactions_bought = relationship("Transaction", foreign_keys="[Transaction.buyer_id]", back_populates="buyer")

 