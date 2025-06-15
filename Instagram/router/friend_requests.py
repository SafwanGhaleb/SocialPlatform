from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from Instagram.database import get_db
from Instagram.models import FriendRequest, FriendRequestStatus
from Instagram.schemas import FriendRequestUpdate, FriendRequestCreate, FriendRequestAction

router = APIRouter(prefix="/friendrequests", tags=["friendrequests"])

@router.post("/friend-request")
def send_friend_request(request: FriendRequestCreate, db: Session = Depends(get_db)):
    try:
        # Check if a request already exists
        existing = db.query(FriendRequest).filter_by(
            sender_id=request.sender_id,
            receiver_id=request.receiver_id
        ).first()

        if existing:
            if existing.status == FriendRequestStatus.pending:
                raise HTTPException(status_code=400, detail="Friend request already sent")
            elif existing.status in [FriendRequestStatus.accepted, FriendRequestStatus.rejected]:
                db.delete(existing)
                db.commit()

        #  Now create a new request
        new_request = FriendRequest(
            sender_id=request.sender_id,
            receiver_id=request.receiver_id,
            status=FriendRequestStatus.pending
        )
        db.add(new_request)
        db.commit()
        db.refresh(new_request)

        return {"message": "Friend request sent", "request_id": new_request.id}

    except Exception as e:
        print("❌ Error in send_friend_request:", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/friend-requests/received/{user_id}")
def get_received_requests(user_id: int, db: Session = Depends(get_db)):
    requests = db.query(FriendRequest).filter_by(
        receiver_id=user_id,
        status=FriendRequestStatus.pending
    ).all()

    return [
        {
            "request_id": req.id,
            "from_user_id": req.sender_id,
            "status": req.status
        }
        for req in requests
    ]


@router.get("/friends/{user_id}")
def list_friends(user_id: int, db: Session = Depends(get_db)):
    accepted_requests = db.query(FriendRequest).filter(
        FriendRequest.status == FriendRequestStatus.accepted,
        or_(
            FriendRequest.sender_id == user_id,
            FriendRequest.receiver_id == user_id
        )
    ).all()

    friend_ids = []
    for req in accepted_requests:
        if req.sender_id == user_id:
            friend_ids.append(req.receiver_id)
        else:
            friend_ids.append(req.sender_id)

    return {"user_id": user_id, "friends": friend_ids}


@router.put("/friend-request/{request_id}")
def update_friend_request(request_id: int,
                          update: FriendRequestUpdate,
                          db: Session = Depends(get_db)):
    friend_request = db.query(FriendRequest).filter_by(id=request_id).first()

    if not friend_request:
        raise HTTPException(status_code=404, detail="Friend request not found")

    if friend_request.status != FriendRequestStatus.pending:
        raise HTTPException(status_code=400, detail="Request already responded to")

    if update.action == FriendRequestAction.accept:
        friend_request.status = FriendRequestStatus.accepted
    elif update.action == FriendRequestAction.reject:
        friend_request.status = FriendRequestStatus.rejected
    elif update.action == FriendRequestAction.revoke:
        db.delete(friend_request)
        db.commit()
        return {"message": "Friend request revoked"}
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    db.commit()
    return {"message": f"Friend request {update.action}ed"}


@router.delete("/friend-request/{request_id}/cancel")
def cancel_friend_request(request_id: int, sender_id: int, db: Session = Depends(get_db)):
    friend_request = db.query(FriendRequest).filter_by(id=request_id).first()

    if not friend_request:
        raise HTTPException(status_code=404, detail="Friend request not found")

    if friend_request.status != FriendRequestStatus.pending:
        raise HTTPException(status_code=400, detail="Cannot cancel — already accepted or rejected")

    if friend_request.sender_id != sender_id:
        raise HTTPException(status_code=403, detail="You can only cancel your own friend requests")

    db.delete(friend_request)
    db.commit()
    return {"message": "Friend request cancelled"}