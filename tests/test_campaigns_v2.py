import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.api.auth import get_current_user
from app.models.campaign import CampaignV2, CampaignStatusV2, CampaignTypeV2
from app.models.user import User
import os
from datetime import datetime, timedelta

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_campaigns_v2.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def override_get_current_user():
    return User(id=1, mobile="1234567890", role="admin")

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    # Seed a campaign
    camp = CampaignV2(
        id="camp1",
        title="Predict and Win",
        type=CampaignTypeV2.PREDICTION,
        status=CampaignStatusV2.ACTIVE,
        start_date=datetime.now() - timedelta(days=1),
        end_date=datetime.now() + timedelta(days=1),
        fields=[],
        rules=["Rule 1"],
        winners=[],
        results_summary="Coming soon"
    )
    db.add(camp)
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_campaigns_v2.db"):
        os.remove("./test_campaigns_v2.db")

client = TestClient(app)

def test_list_campaigns():
    response = client.get("/api/campaigns")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Predict and Win"

def test_get_active_campaigns():
    response = client.get("/api/campaigns/active")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_campaign_details():
    response = client.get("/api/campaigns/camp1")
    assert response.status_code == 200
    assert response.json()["id"] == "camp1"

def test_participate():
    payload = {
        "responses": {"score": "2-1"}
    }
    response = client.post("/api/campaigns/camp1/participate", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "SUBMITTED"

def test_participate_duplicate():
    payload = {
        "responses": {"score": "2-1"}
    }
    response = client.post("/api/campaigns/camp1/participate", json=payload)
    assert response.status_code == 403
    assert "Already participated" in response.json()["detail"]

def test_get_my_participations():
    response = client.get("/api/campaigns/my-participations")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_my_campaign_participation():
    response = client.get("/api/campaigns/camp1/my-participation")
    assert response.status_code == 200
    assert response.json()["campaignId"] == "camp1"

def test_get_results():
    response = client.get("/api/campaigns/camp1/results")
    assert response.status_code == 200
    data = response.json()
    assert "responses" in data
    assert "total_participations" in data
