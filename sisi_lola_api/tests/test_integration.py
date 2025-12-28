import pytest
from fastapi.testclient import TestClient
from sisi_lola_api.app.main_updated import app
from sisi_lola_api.app.database import Base, engine, SessionLocal, Role

@pytest.fixture
def client():
    # Force clean DB for integration tests
    from sisi_lola_api.app.database import engine
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Enable startup events (like init_db)
    with TestClient(app) as c:
        yield c
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)

def test_full_workflow(client):
    """Test complete workflow: register -> login -> create asset -> approve content"""
    
    # 1. Register user
    register_response = client.post("/api/v2/auth/register", json={
        "email": "workflow@test.com",
        "password": "Test123!",
        "roles": ["SUPER_ADMIN"]
    })
    assert register_response.status_code == 201
    
    # 2. Login
    login_response = client.post("/api/v2/auth/login", json={
        "email": "workflow@test.com",
        "password": "Test123!"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Create asset
    asset_response = client.post("/api/v2/control/assets", headers=headers, json={
        "category": "AVATAR_DNA",
        "subcategory": "Reference",
        "filename": "test.png",
        "url": "https://test.com/test.png",
        "metadata": {}
    })
    assert asset_response.status_code == 200
    asset_id = asset_response.json()["asset_id"]
    
    # 4. Update asset status
    status_response = client.put(f"/api/v2/control/assets/{asset_id}/status", 
                                  headers=headers, 
                                  params={"status": "approved"})
    assert status_response.status_code == 200
    
    # 5. Add content to queue
    content_response = client.post("/api/v2/control/content/queue", headers=headers, json={
        "title": "Test Video",
        "script": "Test script content",
        "platform": "youtube",
        "metadata": {}
    })
    assert content_response.status_code == 200
    content_id = content_response.json()["content_id"]
    
    # 6. Approve content
    approve_response = client.put(f"/api/v2/control/content/{content_id}/approve", headers=headers)
    assert approve_response.status_code == 200
    
    # 7. Check dashboard
    dashboard_response = client.get("/api/v2/control/analytics/dashboard", headers=headers)
    assert dashboard_response.status_code == 200
    data = dashboard_response.json()
    assert data["assets"]["total"] == 1
    assert data["content"]["queue_size"] >= 0

def test_api_health(client):
    """Test API is responding"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert "system_status" in response.json()
    assert response.json()["system_status"] == "ONLINE"
