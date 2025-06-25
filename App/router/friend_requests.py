
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from App.models.user_models import FriendRequest, FriendRequestStatus, Friendship, User
from App.schemas.user_schemas import FriendRequestUpdate, FriendRequestAction
from App.core.security import get_current_user
from App.models.user_models import User
from App.db.database import get_db
from App.schemas.user_schemas import FriendRequestCreate



router = APIRouter(prefix="/friendrequests", tags=["Friend Requests"])

# Sends a friend request from the current user to the specified receiver.
@router.post("/friend-request")
def send_friend_request(
    request: FriendRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sender_id = current_user.id

    if sender_id == request.receiver_id:
        raise HTTPException(status_code=400, detail="Cannot send request to yourself.")

    existing = db.query(FriendRequest).filter_by(
        sender_id=sender_id,
        receiver_id=request.receiver_id
    ).first()

    if existing:
        if existing.status == FriendRequestStatus.pending:
            raise HTTPException(status_code=400, detail="Friend request already sent")
        elif existing.status == FriendRequestStatus.accepted:
            raise HTTPException(status_code=400, detail="Friend request already accepted")
        elif existing.status == FriendRequestStatus.rejected:
            db.delete(existing)
            db.commit()

    new_request = FriendRequest(
        sender_id=sender_id,
        receiver_id=request.receiver_id,
        status=FriendRequestStatus.pending
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return {
        "message": "Friend request sent",
        "request_id": new_request.id,
        "sender_id": sender_id
    }

# Returns a list of the current user's confirmed friends.
@router.get("/friends/{user_id}")
def list_friends(user_id: int, db: Session = Depends(get_db)):
    """Get a list of friend IDs for a given user"""
    accepted = db.query(FriendRequest).filter(
        FriendRequest.status == FriendRequestStatus.accepted,
        or_(
            FriendRequest.sender_id == user_id,
            FriendRequest.receiver_id == user_id
        )
    ).all()

    friend_ids = [
        req.receiver_id if req.sender_id == user_id else req.sender_id
        for req in accepted
    ]
    return {"user_id": user_id, "friends": friend_ids}

# Accepts a pending friend request from another user.
@router.put("/friend-request/{request_id}")
def update_friend_request(
    request_id: int,
    update: FriendRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Accept, reject, or revoke a friend request — with proper authorization"""
    friend_request = db.query(FriendRequest).filter_by(id=request_id).first()

    if not friend_request:
        raise HTTPException(status_code=404, detail="Friend request not found")

    if friend_request.status != FriendRequestStatus.pending:
        raise HTTPException(status_code=400, detail="Friend request already handled")

    # 🔐 Action-based permission checks
    if update.action in [FriendRequestAction.accept, FriendRequestAction.reject]:
        if current_user.id != friend_request.receiver_id:
            raise HTTPException(status_code=403, detail="Only the receiver can accept or reject this request")

    elif update.action == FriendRequestAction.revoke:
        if current_user.id != friend_request.sender_id:
            raise HTTPException(status_code=403, detail="Only the sender can revoke this request")
        db.delete(friend_request)
        db.commit()
        return {"message": "Friend request revoked"}

    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    if update.action == FriendRequestAction.accept:
        print("🔁 Friend request accepted")

        friend_request.status = FriendRequestStatus.accepted

        if not db.query(Friendship).filter_by(user_id=friend_request.sender_id,
                                              friend_id=friend_request.receiver_id).first():
            print("➕ Creating friendship: sender -> receiver")
            db.add(
                Friendship(user_id=friend_request.sender_id, friend_id=friend_request.receiver_id, status="accepted"))
        else:
            print("ℹ️ Already exists: sender -> receiver")

        if not db.query(Friendship).filter_by(user_id=friend_request.receiver_id,
                                              friend_id=friend_request.sender_id).first():
            print("➕ Creating friendship: receiver -> sender")
            db.add(
                Friendship(user_id=friend_request.receiver_id, friend_id=friend_request.sender_id, status="accepted"))
        else:
            print("ℹ️ Already exists: receiver -> sender")

    elif update.action == FriendRequestAction.reject:
        print("❌ Friend request rejected")
        friend_request.status = FriendRequestStatus.rejected

    db.commit()
    print("✅ Database committed")
    return {"message": f"Friend request {update.action}ed successfully"}


# Cancels a pending friend request.
# Only the sender or receiver of the request can cancel it, and only if it's still pending.
# Raises 403 if unauthorized, 404 if not found, or 400 if already accepted/declined.
@router.delete("/friend-request/{request_id}/cancel")
def cancel_friend_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    friend_request = db.query(FriendRequest).filter_by(id=request_id).first()

    if not friend_request:
        raise HTTPException(status_code=404, detail="Friend request not found")

    # Only allow sender or receiver to cancel
    if current_user.id not in [friend_request.sender_id, friend_request.receiver_id]:
        raise HTTPException(status_code=403, detail="You are not authorized to cancel this request")

    # Only pending requests can be cancelled
    if friend_request.status != FriendRequestStatus.pending:
        raise HTTPException(status_code=400, detail="Cannot cancel — request already handled")

    db.delete(friend_request)
    db.commit()
    return {"message": "Friend request cancelled"}
