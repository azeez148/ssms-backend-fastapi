import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.api.auth import get_current_user, get_current_user_admin
from app.models.campaign import CampaignV2, CampaignStatusV2, CampaignTypeV2, CampaignParticipation
from app.models.user import User
import os
from datetime import datetime, timedelta

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_campaign_v2_reset.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def override_get_current_user():
    return User(id="1", mobile="1234567890", role="admin")

def override_get_current_user_admin():
    return User(id="1", mobile="1234567890", role="admin")

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user
app.dependency_overrides[get_current_user_admin] = override_get_current_user_admin

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    # Seed a campaign
    camp = CampaignV2(
        id="camp_reset",
        title="Reset Test",
        type=CampaignTypeV2.prediction,
        status=CampaignStatusV2.active,
        start_date=datetime.now() - timedelta(days=1),
        end_date=datetime.now() + timedelta(days=1),
    )
    db.add(camp)

    # Add a user
    user = User(id="1", mobile="1234567890", role="admin")
    db.add(user)
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_campaign_v2_reset.db"):
        os.remove("./test_campaign_v2_reset.db")

client = TestClient(app)

def test_reset_participants():
    # 1. Participate in the campaign
    payload = {
        "responses": {"score": "2-1"}
    }
    resp = client.post("/api/campaigns/camp_reset/participate", json=payload)
    assert resp.status_code == 200

    # Verify participation exists in DB
    db = TestingSessionLocal()
    count = db.query(CampaignParticipation).filter(CampaignParticipation.campaign_id == "camp_reset").count()
    assert count == 1
    db.close()

    # 2. Call reset endpoint
    resp = client.post("/api/campaigns/camp_reset/reset-participants")
    assert resp.status_code == 200
    assert resp.json()["message"] == "All participants have been removed from the campaign"

    # 3. Verify participation is gone
    db = TestingSessionLocal()
    count = db.query(CampaignParticipation).filter(CampaignParticipation.campaign_id == "camp_reset").count()
    assert count == 0
    db.close()

def test_reset_non_existent_campaign():
    resp = client.post("/api/campaigns/non_existent/reset-participants")
    assert resp.status_code == 404
