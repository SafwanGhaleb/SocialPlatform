from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from App.db.database import get_db
from App.models.user_models import Friendship
from App.models.post import Post

router = APIRouter()

@router.get("/feed/{user_id}")
def get_friends_posts(user_id: int, db: Session = Depends(get_db)):
    # Get accepted friend IDs
    friends = db.query(Friendship).filter_by(user_id=user_id, status="accepted").all()
    friend_ids = [f.friend_id for f in friends]

    # Get posts from friends
    posts = db.query(Post).filter(Post.user_id.in_(friend_ids)).order_by(Post.timestamp.desc()).all()
    return posts