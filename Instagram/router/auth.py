from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from Instagram.database import get_db
from Instagram.models import User
from Instagram.schemas import UserCreate, UserLogin
from Instagram.security import hash_password, verify_password
from Instagram.schemas import UserResponse
from Instagram.schemas import UserUpdate


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")

        if db.query(User).filter(User.username == user.username).first():
            raise HTTPException(status_code=400, detail="Username already taken")

        new_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hash_password(user.password)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "User registered successfully", "user_id": new_user.id}

    except Exception as e:
        print("❌ Registration error:", e)
        raise HTTPException(status_code=500, detail="Registration failed")


@router.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "user_id": db_user.id}

@router.get("/profile/{user_id}", response_model=UserResponse)
def get_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/profile/{user_id}")
def update_profile(user_id: int, update: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.username = update.username
    user.email = update.email
    db.commit()
    db.refresh(user)

    return {"message": "Profile updated", "user": {"username": user.username, "email": user.email}}
@router.delete("/profile/{user_id}")
def delete_account(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "Account deleted"}
