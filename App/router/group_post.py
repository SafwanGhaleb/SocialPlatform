from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from App.db.database import get_db
from App.core.security import get_current_user
from App.models.group_post import GroupMember
from App.models.user_models import User
from App.models.group_post import GroupPost

router = APIRouter(
    prefix="/groups",
    tags=["Group Posts"]
)


@router.post("/groups/{group_id}/join")
def join_group(group_id: int, user_id: int, db: Session = Depends(get_db)):
    exists = db.query(GroupMember).filter_by(group_id=group_id, user_id=user_id).first()
    if exists:
        raise HTTPException(status_code=400, detail="Already a member")
    member = GroupMember(group_id=group_id, user_id=user_id)
    db.add(member)
    db.commit()
    return {"message": "Joined group"}

@router.post("/groups/{group_id}/post")
def post_in_group(group_id: int, user_id: int, content: str, db: Session = Depends(get_db)):
    member = db.query(GroupMember).filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        raise HTTPException(status_code=403, detail="Not a member")
    post = GroupPost(group_id=group_id, user_id=user_id, content=content)
    db.add(post)
    db.commit()
    return {"message": "Post added"}

@router.get("/groups/{group_id}/posts")
def get_group_posts(group_id: int, db: Session = Depends(get_db)):
    posts = db.query(GroupPost).filter_by(group_id=group_id).order_by(GroupPost.timestamp.desc()).all()
    return posts

@router.delete("/{group_id}/kick/{user_id}")
def kick_member(
    group_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    admin = db.query(GroupMember).filter_by(
        group_id=group_id, user_id=current_user.id, is_admin=True
    ).first()
    if not admin:
        raise HTTPException(status_code=403, detail="You are not an admin")

    target = db.query(GroupMember).filter_by(group_id=group_id, user_id=user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not in group")

    db.delete(target)
    db.commit()
    return {"message": "User removed"}