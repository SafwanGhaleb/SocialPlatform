from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from App.db.database import get_db
from App.core.security import get_current_user
from App.models.user_models import User
from App.models.post import Post
from App.schemas.post import PostResponse, PostCreate
from typing import List

router = APIRouter(prefix="/wall")

@router.post("/", response_model=PostResponse)
def create_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    new_post = Post(user_id=user.id, content=post.content, image_url=post.image_url)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/my", response_model=List[PostResponse])
def get_my_wall(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    posts = (
        db.query(Post)  # ✅ use the directly imported Post model
        .filter(Post.user_id == user.id)
        .order_by(Post.created_at.desc())
        .all()
    )
    return posts