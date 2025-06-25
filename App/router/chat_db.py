from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from App.db.database import get_db
from App.core.security import get_current_user
from App.models.user_models import User
from App.models.message import Message
from App.schemas.message import MessageCreate, MessageResponse

router = APIRouter(
    prefix="/chat",
    tags=["Simple Chat"]
)

# Sends a chat message from the current user to another user and saves it in the database.
@router.post("/send", response_model=MessageResponse)
def send_message(
    msg: MessageCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    message = Message(sender_id=user.id, receiver_id=msg.receiver_id, content=msg.content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

# Retrieves all chat messages between the current user and the specified friend.
@router.get("/history/{friend_id}", response_model=List[MessageResponse])
def get_chat_history(
    friend_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    messages = db.query(Message).filter(
        ((Message.sender_id == user.id) & (Message.receiver_id == friend_id)) |
        ((Message.sender_id == friend_id) & (Message.receiver_id == user.id))
    ).order_by(Message.timestamp.asc()).all()
    return messages