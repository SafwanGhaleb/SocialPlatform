from pydantic import BaseModel
from datetime import datetime

# Message creation schema (input)
class MessageCreate(BaseModel):
    receiver_id: int
    content: str

# Message response schema (output)
class MessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    timestamp: datetime


    class Config:
        from_attributes = True