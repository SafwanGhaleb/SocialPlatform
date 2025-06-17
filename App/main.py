from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from App.router import auth, friend_requests, wall, feed, group_post, chat_db
from App.db.database import create_tables

import sys
import os

# Enable relative imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Initialize FastAPI app
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to SocialConnect API!"}

# Call once to initialize the tables
create_tables()

# Register routes
app.include_router(auth.router, tags=["Auth"])
app.include_router(friend_requests.router, tags=["Friend Requests"])
app.include_router(wall.router, tags=["Wall"])
app.include_router(feed.router, tags=["Feed"])
app.include_router(group_post.router, tags=["Group Posts"])
app.include_router(chat_db.router, tags=["Simple Chat"])

# ✅ Inject security schema into OpenAPI docs
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