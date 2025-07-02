import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from App.main import app
from App.db.database import Base, get_db

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Setup test DB
SQLALCHEMY_TEST_DB_URL = "sqlite:///./test_user_auth.db"
engine = create_engine(SQLALCHEMY_TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency override
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function")
def cleanup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def test_user_registration_and_login(cleanup_db):
    registration_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "securepassword"
    }
    response = client.post("/auth/register", json=registration_data)
    assert response.status_code == 200
    assert response.json()["message"] == "User registered successfully"
    assert "user_id" in response.json()

    login_data = {
        "username": "testuser",
        "password": "securepassword"
    }
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_duplicate_user_registration(cleanup_db):
    client.post("/auth/register", json={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "password123"
    })

    response = client.post("/auth/register", json={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "password123"
    })
    assert response.status_code == 400
    assert "already" in response.json()["detail"]


def test_invalid_login_credentials(cleanup_db):
    client.post("/auth/register", json={
        "username": "wronguser",
        "email": "wronguser@example.com",
        "password": "correctpassword"
    })

    response = client.post("/auth/login", data={
        "username": "wronguser",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_token_access_to_profile(cleanup_db):
    register = client.post("/auth/register", json={
        "username": "secureuser",
        "email": "secureuser@example.com",
        "password": "pass1234"
    })
    user_id = register.json()["user_id"]

    login = client.post("/auth/login", data={
        "username": "secureuser",
        "password": "pass1234"
    })
    token = login.json()["access_token"]

    response = client.get(f"/auth/profile/{user_id}", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert response.json()["id"] == user_id
