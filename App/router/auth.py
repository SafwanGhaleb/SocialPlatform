from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from App.db.database import get_db
from App.models.user_models import User
from App.schemas.user_schemas import UserCreate, UserLogin
from App.core.security import hash_password, verify_password
from App.schemas.user_schemas import UserResponse
from App.schemas.user_schemas import UserUpdate
from fastapi.security import OAuth2PasswordRequestForm
from App.core.security import create_access_token


router = APIRouter(prefix="/auth")

# Registers a new user and stores their credentials securely in the database.

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
        print("Registration Error:", e)  # ✅ Log actual error in terminal
        raise HTTPException(status_code=500, detail="Registration failed")

    except Exception as e:
        print("❌ Registration error:", e)
        raise HTTPException(status_code=500, detail="Registration failed")

# Authenticates a user and returns a JWT access token upon successful login.

@router.post("/login")
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == form_data.username).first()
    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # ✅ Create access token
    access_token = create_access_token(data={"user_id": db_user.id})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


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
