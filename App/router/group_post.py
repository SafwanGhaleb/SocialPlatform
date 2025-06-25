from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from App.db.database import get_db
from App.core.security import get_current_user
from App.models.group_post import GroupMember, Group
from App.models.user_models import User
from App.models.group_post import GroupPost
from typing import Optional

router = APIRouter(
    prefix="/groups",
    tags=["Group Posts"]
)


# Creates a new group and sets the current user as the admin.

@router.post("/groups/create")
def create_group(
    name: str,
    description: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if group name exists
    existing = db.query(Group).filter_by(name=name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Group name already taken")

    # Create group
    group = Group(name=name, description=description)
    db.add(group)
    db.commit()
    db.refresh(group)

    # Add creator as admin member
    admin_member = GroupMember(group_id=group.id, user_id=current_user.id, is_admin=True)
    db.add(admin_member)
    db.commit()

    return {
        "message": "Group created",
        "group_id": group.id,
        "created_by": current_user.id
    }

# Promotes a group member to admin — only current admins can do this.
@router.post("/{group_id}/promote/{user_id}")
def promote_to_admin(
    group_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if current user is admin
    admin = db.query(GroupMember).filter_by(
        group_id=group_id, user_id=current_user.id, is_admin=True
    ).first()
    if not admin:
        raise HTTPException(status_code=403, detail="You are not an admin")

    # Check if the target user is a member
    member = db.query(GroupMember).filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="User is not a member of the group")

    # Promote to admin
    member.is_admin = True
    db.commit()
    return {"message": f"User {user_id} promoted to admin"}

# Adds a user to a group as a member (if not already joined).
@router.post("/groups/{group_id}/join")
def join_group(group_id: int, user_id: int, db: Session = Depends(get_db)):
    exists = db.query(GroupMember).filter_by(group_id=group_id, user_id=user_id).first()
    if exists:
        raise HTTPException(status_code=400, detail="Already a member")
    member = GroupMember(group_id=group_id, user_id=user_id)
    db.add(member)
    db.commit()
    return {"message": "Joined group"}

# Posts content to a group by a group member.
@router.post("/groups/{group_id}/post")
def post_in_group(group_id: int, user_id: int, content: str, db: Session = Depends(get_db)):
    member = db.query(GroupMember).filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        raise HTTPException(status_code=403, detail="Not a member")
    post = GroupPost(group_id=group_id, user_id=user_id, content=content)
    db.add(post)
    db.commit()
    return {"message": "Post added"}

# Retrieves all posts within a specific group.
@router.get("/groups/{group_id}/posts")
def get_group_posts(group_id: int, db: Session = Depends(get_db)):
    posts = db.query(GroupPost).filter_by(group_id=group_id).order_by(GroupPost.timestamp.desc()).all()
    return posts

# Removes a user from a group — only admins are allowed.
@router.delete("/{groups}/kick/{user_id}")
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


