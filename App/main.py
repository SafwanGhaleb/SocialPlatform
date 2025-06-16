from fastapi import  FastAPI
from App.router import friend_requests
from App.router import auth
from App.db.database import create_tables
from App.router import wall
from App.models.user_models import User


import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
create_tables()
app = FastAPI()
@app.get("/")
def read_root():
    return {"message": "Welcome to SocialConnect API!"}
# Ensure tables are created (optional in production)

app.include_router(auth.router)
app.include_router(friend_requests.router)
app.include_router(wall.router)


create_tables()
