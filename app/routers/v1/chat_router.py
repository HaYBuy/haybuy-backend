from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models.Users.User import User
from app.db.models.Chats.chat import Chat
from app.db.models.Chats.chat_member import ChatMember
from app.db.models.Chats.chat_message import ChatMessage
from app.schemas.chat_schema import ChatCreate, ChatResponse
from app.schemas.chat_message_schema import (
    ChatMessageCreate,
    ChatMessageResponse,
)

router = APIRouter(prefix="/chats", tags=["Chats"])


# สร้าง Chat ใหม่
@router.post("/", response_model=ChatResponse)
def create_chat(
    chat_data: ChatCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):

    user = db.get(User, chat_data.participant_id)
    if not user:
        raise HTTPException(status_code=404, detail="Participant not found")

    new_chat = Chat()
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)

    members = [
        ChatMember(chat_id=new_chat.id, user_id=current_user["id"]),
        ChatMember(chat_id=new_chat.id, user_id=chat_data.participant_id),
    ]

    db.add_all(members)
    db.commit()

    return new_chat


# ส่งข้อความ
@router.post("/messages", response_model=ChatMessageResponse)
def send_message(
    message_data: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    chat = db.get(Chat, message_data.chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    is_member = (
        db.query(ChatMember)
        .filter(
            ChatMember.chat_id == message_data.chat_id,
            ChatMember.user_id == current_user["id"],
        )
        .first()
    )

    if not is_member:
        raise HTTPException(status_code=403, detail="You are not a member of this chat")

    if not message_data.image_url and not message_data.text:
        raise HTTPException(status_code=400, detail="message empyty")

    msg = ChatMessage(
        chat_id=message_data.chat_id,
        sender_id=current_user["id"],
        text=message_data.text,
        image_url=message_data.image_url,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


# ดึงข้อความทั้งหมดของ chat
@router.get("/{chat_id}/messages", response_model=List[ChatMessageResponse])
def get_chat_messages(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):

    chat = db.get(Chat, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    is_member = (
        db.query(ChatMember)
        .filter(ChatMember.chat_id == chat_id, ChatMember.user_id == current_user["id"])
        .first()
    )

    if not is_member:
        raise HTTPException(status_code=403, detail="You are not a member of this chat")

    return chat.messages


@router.get("/my", response_model=List[ChatResponse])
def get_user_chats(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):

    chats = (
        db.query(Chat)
        .join(ChatMember)
        .filter(ChatMember.user_id == current_user["id"])
        .order_by(Chat.updated_at.desc())
        .all()
    )
    return chats
