import pytest
from fastapi.testclient import TestClient
from app.main_updated import app
from app.database import Base, engine, SessionLocal
from app.auth import get_password_hash

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(client):
    from app.database import User, Role
    db = SessionLocal()
    
    role = Role(name="VIEWER", description="Test", permissions=["content:read"])
    db.add(role)
    db.commit()
    
    user = User(email="test@test.com", password_hash=get_password_hash("test123"))
    db.add(user)
    db.commit()
    db.refresh(user)
    user.roles.append(role)
    db.commit()
    db.close()
    return {"email": "test@test.com", "password": "test123"}

def test_login_success(client, test_user):
    response = client.post("/api/v2/auth/login", json=test_user)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_login_invalid_credentials(client):
    response = client.post("/api/v2/auth/login", json={"email": "wrong@test.com", "password": "wrong"})
    assert response.status_code == 401

def test_get_current_user(client, test_user):
    login_response = client.post("/api/v2/auth/login", json=test_user)
    token = login_response.json()["access_token"]
    
    response = client.get("/api/v2/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == test_user["email"]

def test_unauthorized_access(client):
    response = client.get("/api/v2/auth/me")
    assert response.status_code == 403
