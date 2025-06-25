
from App.core.security import get_current_user
from App.models.user_models import User
from App.schemas.post import PostCreate
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from App.db.database import get_db
from App.models.user_models import Friendship
from App.models.post import Post
from App.schemas.post import PostResponse


router = APIRouter(prefix="/wall")

# Creates a new public wall post for the current user.
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

# Retrieves all wall posts made by the user and their friends.
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


# Retrieves all posts made by the friends of the given user.
# The user ID is used to find accepted friendships, and posts are filtered by those friend IDs.
# Returns an empty list if the user has no friends or no posts.
@router.get("/{user_id}/friends-posts", response_model=List[PostResponse])
def get_friends_posts(user_id: int, db: Session = Depends(get_db)):
    # Get IDs of accepted friends for the user
    friend_ids = db.query(Friendship.friend_id).filter(
        Friendship.user_id == user_id,
        Friendship.status == "accepted"
    ).all()

    # Convert list of tuples to flat list
    friend_ids = [fid[0] for fid in friend_ids]

    if not friend_ids:
        return []

    # Fetch posts made by those friends
    posts = db.query(Post).filter(
        Post.user_id.in_(friend_ids)
    ).order_by(Post.created_at.desc()).all()

    return posts
