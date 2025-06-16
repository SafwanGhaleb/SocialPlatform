from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PostCreate(BaseModel):
    content: Optional[str] = None
    image_url: Optional[str] = None

class PostResponse(BaseModel):
    id: int
    user_id: int
    content: Optional[str]
    image_url: Optional[str]
    created_at: datetime

    model_config = {
        "from_attributes": True
    }