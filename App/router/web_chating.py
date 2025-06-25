from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends
from sqlalchemy.orm import Session
from App.db.database import get_db
from App.core.security import get_current_user_from_token
from App.models.user_models import User
from App.models.message import Message
from datetime import datetime
from typing import Dict

router = APIRouter()

active_connections: Dict[int, WebSocket] = {}

"""
Establishes a real-time WebSocket chat session between two users.

Clients must provide:
- A valid JWT token in the query string (`?token=...`)
- A receiver user ID in the URL path

Once connected, messages are exchanged and stored in the database.
"""

@router.websocket("/ws/chat/{receiver_id}")
async def chat_websocket(websocket: WebSocket, receiver_id: int, db: Session = Depends(get_db)):
    """
    Real-time chat WebSocket.

    ✅ Steps to test:
    1. Open http://localhost:8000/static/chat.html in two browser tabs.
    2. In Tab 1: enter token for user 1 and receiver_id = 2.
    3. In Tab 2: enter token for user 2 and receiver_id = 1.
    4. Press Connect in both and start chatting!
    """
    try:
        token = websocket.query_params.get("token")
        if not token:
            print("⚠️ No token provided")
            await websocket.close(code=1008)
            return

        user: User = get_current_user_from_token(token, db)
        if not user:
            print("❌ Invalid token or user not found")
            await websocket.close(code=1008)
            return

        await websocket.accept()
        print(f"✅ {user.username} connected to chat with {receiver_id}")
        active_connections[user.id] = websocket

        while True:
            data = await websocket.receive_text()
            print(f"📩 Received from {user.id} to {receiver_id}: {data}")

            message = Message(
                sender_id=user.id,
                receiver_id=receiver_id,
                content=data,
                timestamp=datetime.utcnow()
            )
            db.add(message)
            db.commit()

            if receiver_id in active_connections:
                await active_connections[receiver_id].send_text(f"{user.username}: {data}")

    except WebSocketDisconnect:
        print(f"🔌 Disconnected: {user.id}")
        active_connections.pop(user.id, None)
    except Exception as e:
        print(f"❗ WebSocket error: {e}")
        await websocket.close(code=1011)

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/chat-launcher", tags=["Simple Chat"], response_class=HTMLResponse)
def launch_chat_ui():
    """
    🟢 Launch Dual-Tab Chat Testing UI

    Opens two separate browser tabs of the real-time WebSocket chat interface to simulate two users.

    🧪 Use this for local testing with JWT tokens and receiver IDs.

    👉 open manually: http://localhost:8000/static/chat.html
    """
    return """
    <html>
        <head>
            <title>Launch Chat</title>
        </head>
        <body style="font-family: Arial; text-align: center; padding-top: 100px;">
            <h2>💬 Simulate Real-Time Chat</h2>
            <p>This will open two chat windows in separate tabs — to simulate user-to-user messaging.</p>
            <button id="launchBtn" style="padding: 12px 24px; font-size: 18px; cursor: pointer;">
                🧪 Open Chat in Two Tabs
            </button>

            <script>
                document.getElementById("launchBtn").addEventListener("click", () => {
                    window.open('/static/chat.html', '_blank');
                    window.open('/static/chat.html', '_blank');
                });
            </script>
        </body>
    </html>
    """

