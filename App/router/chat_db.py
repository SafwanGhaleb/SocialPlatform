from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from App.db.database import get_db
from App.core.security import get_current_user
from App.models.user_models import User, Friendship
from App.models.message import Message
from App.schemas.message import MessageCreate, MessageResponse
from sqlalchemy import and_, or_

router = APIRouter(
    prefix="/chat",
    tags=["Simple Chat"]
)

@router.post("/send", response_model=MessageResponse)
def send_message(
    msg: MessageCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Check if receiver exists
    receiver = db.query(User).filter(User.id == msg.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")

    # Check if users are friends
    is_friend = db.query(Friendship).filter(
        and_(
            or_(
                and_(Friendship.user_id == user.id, Friendship.friend_id == msg.receiver_id),
                and_(Friendship.user_id == msg.receiver_id, Friendship.friend_id == user.id)
            ),
            Friendship.status == "accepted"
        )
    ).first()
    print("🔍 FRIENDSHIP QUERY DEBUG")
    print("Authenticated user ID:", user.id)
    print("Receiver ID:", msg.receiver_id)

    results = db.query(Friendship).all()
    for f in results:
        print(f"Friendship: {f.user_id} ↔ {f.friend_id}, status: {f.status}")

    print("Friendship match found?", bool(is_friend))
    if not is_friend:
        raise HTTPException(status_code=403, detail="You are not friends with this user")

    # Save message
    message = Message(sender_id=user.id, receiver_id=msg.receiver_id, content=msg.content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

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
