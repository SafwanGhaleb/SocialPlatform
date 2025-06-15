from sqlalchemy import ForeignKey, Enum as SQLAEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from Instagram.database import Base
import enum
from sqlalchemy import Column, Integer, String

#  Enum for request status
class FriendRequestStatus(str, enum.Enum):
    pending  = "pending"
    accepted = "accepted"
    rejected = "rejected"
    revoked  =  "revoked"

#  User table

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

#  Friend request table
class FriendRequest(Base):
    __tablename__ = 'friend_requests'
    __table_args__ = (UniqueConstraint('sender_id', 'receiver_id', name='unique_friend_request'),)

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey('users.id'))
    receiver_id = Column(Integer, ForeignKey('users.id'))
    status = Column(SQLAEnum(FriendRequestStatus), default=FriendRequestStatus.pending)

    sender = relationship('User', foreign_keys=[sender_id])
    receiver = relationship('User', foreign_keys=[receiver_id])
