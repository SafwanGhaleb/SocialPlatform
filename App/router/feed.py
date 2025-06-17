from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from App.db.database import get_db
from App.models.user_models import Friendship
from App.models.post import Post
from App.schemas.post import PostResponse

router = APIRouter(prefix="/feed", tags=["Feed"])

@router.get("/{user_id}", response_model=List[PostResponse])
def get_friends_posts(user_id: int, db: Session = Depends(get_db)):
    # Get accepted friends
    friend_ids = db.query(Friendship.friend_id).filter(
        Friendship.user_id == user_id,
        Friendship.status == "accepted"
    ).all()

    # Flatten list of tuples to a list of integers
    friend_ids = [fid[0] for fid in friend_ids]

    if not friend_ids:
        return []

    # Get posts made by those friends
    posts = db.query(Post).filter(
        Post.user_id.in_(friend_ids)
    ).order_by(Post.created_at.desc()).all()

    return posts
