from fastapi import  FastAPI
from Instagram.router import friend_requests
from Instagram.router import auth
from Instagram.database import create_tables


import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
app = FastAPI()

# Ensure tables are created (optional in production)

app.include_router(auth.router)  
app.include_router(friend_requests.router)

create_tables()
