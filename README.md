
Hello,

📘 SocialConnect — FastAPI-Based Social Network Backend
SocialConnect is a backend system built with FastAPI that supports core social networking features such as:

✅ User authentication and JWT-based login

👥 Friend request management (send, accept, cancel)

📃 Wall posts (public)

👨‍👩‍👧‍👦 Group creation, membership, and admin roles

💬 Private chat using REST and real-time WebSocket

🌐 HTML-based chat interface and Swagger UI

🗂️ Project Structure

SocialConnect/
├── App/
│   ├── main.py
│
│   ├── db/
│   │   └── database.py
│
│   ├── models/
│   │   ├── user_models.py
│   │   ├── group_post.py
│   │   ├── message.py
│   │   ├── post.py                
│
│   ├── schemas/
│   │   ├── user_schemas.py        
│   │   ├── post.py                
│   │   ├── message.py
│
│   ├── core/
│   │   ├── security.py
│   │   ├── config.py
│
│   ├── router/
│   │   ├── auth.py
│   │   ├── friend_requests.py
│   │   ├── wall.py
│   │   ├── group_post.py
│   │   ├── chat_db.py
│   │   ├── web_chating.py
│
│   ├── static/
│   │   └── chat.html              # ✅ No welcome_banner.png yet
│
│   └── __init__.py
│
├── requirements.txt
└── README.md




🚀 Getting Started
1- Clone the repo


git clone https://github.com/your-org/socialconnect.git
cd socialconnect

2- Install dependencies

pip install -r requirements.txt

3- Run the app

uvicorn App.main:app --reload

4- Access the API docs

http://localhost:8000/docs

5- Try the HTML chat interface

http://localhost:8000/chat-launcher

6- ⚙️ Tech Stack
FastAPI – high-performance web framework

SQLAlchemy – ORM for DB access

Pydantic – data validation and serialization

JWT (via python-jose) – secure user authentication

WebSocket – real-time chat communication


After cloning the project, please follow these instructions:

1. Install Uvicorn:
   
   pip install uvicorn
   
2. Run the server:
   
   python -m uvicorn App.main:app --reload

Hello Team.
