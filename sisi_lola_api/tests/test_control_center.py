import pytest
from fastapi.testclient import TestClient
from sisi_lola_api.app.main import app
from sisi_lola_api.app.database import Base, engine, SessionLocal
from sisi_lola_api.app.auth import get_password_hash, create_access_token

@pytest.fixture
def client():
    # Force clean DB
    from sisi_lola_api.app.database import engine
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def admin_token():
    from sisi_lola_api.app.database import User, Role
    db = SessionLocal()
    
    # Use existing role created by init_db
    role = db.query(Role).filter(Role.name == "SUPER_ADMIN").first()
    if not role:
        role = Role(name="SUPER_ADMIN", description="Admin", permissions=["*"])
        db.add(role)
        db.commit()
    
    # Check if user already exists
    user = db.query(User).filter(User.email == "admin@test.com").first()
    if not user:
        user = User(email="admin@test.com", password_hash=get_password_hash("admin123"))
        db.add(user)
        db.commit()
        db.refresh(user)
        user.roles.append(role)
        db.commit()
    
    token = create_access_token({"sub": "admin@test.com", "roles": ["SUPER_ADMIN"]})
    db.close()
    return token

def test_create_asset(client, admin_token):
    response = client.post(
        "/api/v2/control/assets",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "category": "AVATAR_DNA",
            "subcategory": "Reference",
            "filename": "test.png",
            "url": "https://test.com/test.png",
            "metadata": {"resolution": "4K"}
        }
    )
    assert response.status_code == 200
    assert "asset_id" in response.json()

def test_list_assets(client, admin_token):
    response = client.get("/api/v2/control/assets", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert "assets" in response.json()

def test_add_to_content_queue(client, admin_token):
    response = client.post(
        "/api/v2/control/content/queue",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "Test Video",
            "script": "Test script",
            "platform": "youtube",
            "metadata": {}
        }
    )
    assert response.status_code == 200
    assert "content_id" in response.json()

def test_dashboard_metrics(client, admin_token):
    response = client.get("/api/v2/control/analytics/dashboard", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    data = response.json()
    assert "assets" in data
    assert "content" in data
    assert "ml" in data

def test_unauthorized_asset_creation(client):
    response = client.post("/api/v2/control/assets", json={"category": "TEST"})
    assert response.status_code == 401  # No credentials provided
