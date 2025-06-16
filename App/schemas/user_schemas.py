from pydantic import BaseModel, EmailStr
from enum import Enum


class FriendRequestAction(str, Enum):
    accept = "accept"
    reject = "reject"
    revoke = "revoke"

#
class FriendRequestUpdate(BaseModel):
    action: FriendRequestAction

class FriendRequestCreate(BaseModel):
    sender_id: int
    receiver_id: int

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

class Config:
        from_attributes = True

        # Used for login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    username: str
    email: EmailStr
