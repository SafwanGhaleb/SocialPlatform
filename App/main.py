from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from App.router import auth, friend_requests, wall, group_post, chat_db
from App.db.database import create_tables
from App.router import web_chating
from fastapi.responses import HTMLResponse
from fastapi import APIRouter
from fastapi.responses import RedirectResponse
"""
SocialConnect - FastAPI-Based Social Network Backend

This application powers a simple social networking platform with the following features:

- User authentication and registration using JWT tokens
- Friend request management (send, accept, cancel)
- Public wall posting system
- Group creation and group posts with admin privileges
- Private messaging (chat) via REST and real-time WebSocket
- HTML-based real-time chat interface for testing
- Swagger UI for interactive API exploration

The system is modularized using FastAPI routers and follows a clear MVC-like separation:
- `models/`       contains SQLAlchemy database models (Base)
- `schemas/`      contains Pydantic models (BaseModel) for validation and serialization
- `router/`       contains all API route logic, grouped by feature
- `core/`         contains security and configuration utilities
- `static/`       contains frontend assets (like chat.html)

All dependencies are declared in `requirements.txt`, and the app runs using:
    uvicorn App.main:app --reload

Developed for educational and collaborative backend development.
"""
import sys
import os
from fastapi.staticfiles import StaticFiles
app = FastAPI()

app.mount("/static", StaticFiles(directory="App/static"), name="static")
# Enable relative imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from App.main import app

# Initialize FastAPI app

@app.get("/")
def read_root():
    return {"message": "Welcome to SocialConnect FastAPI!"}


# Call once to initialize the tables
create_tables()

# Register routes
app.include_router(auth.router, tags=["Auth"])
app.include_router(friend_requests.router)
app.include_router(wall.router, tags=["Wall"])
app.include_router(group_post.router)
app.include_router(chat_db.router)
app.include_router(web_chating.router)






def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="SocialConnect API",
        version="1.0.0",
        description="API for social interaction platform",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

from fastapi.responses import HTMLResponse

