import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
import os

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_campaigns.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_campaigns.db"):
        os.remove("./test_campaigns.db")

client = TestClient(app)

def test_create_campaign():
    payload = {
        "name": "Summer Tournament",
        "type": "Tournament",
        "shortDescription": "Join our summer tournament!",
        "questions": [
            {
                "questionText": "What is your favorite color?",
                "questionType": "text",
                "isRequired": True,
                "order": 1
            }
        ]
    }
    response = client.post("/campaigns/create", json=payload)
    if response.status_code != 200:
        print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Summer Tournament"
    assert data["slug"] == "summer-tournament"
    assert len(data["questions"]) == 1
    assert data["questions"][0]["questionText"] == "What is your favorite color?"

def test_get_all_campaigns():
    response = client.get("/campaigns/all")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 1

def test_update_campaign_status():
    # First get the campaign created in the previous test
    response = client.get("/campaigns/all")
    campaign_id = response.json()["items"][0]["id"]

    payload = {"status": "Active"}
    response = client.put(f"/campaigns/{campaign_id}/status", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "Active"

def test_campaign_stats():
    response = client.get("/campaigns/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["totalCampaigns"] >= 1
    assert data["activeCampaigns"] >= 1

def test_questions():
    response = client.get("/campaigns/all")
    campaign_id = response.json()["items"][0]["id"]

    # Get questions
    response = client.get(f"/campaigns/{campaign_id}/questions")
    assert response.status_code == 200
    assert len(response.json()) == 1

    # Save new questions (overwrite)
    new_questions = [
        {
            "questionText": "Question 1",
            "questionType": "single_choice",
            "options": ["A", "B"],
            "isRequired": True,
            "order": 0
        },
        {
            "questionText": "Question 2",
            "questionType": "text",
            "isRequired": False,
            "order": 1
        }
    ]
    response = client.post(f"/campaigns/{campaign_id}/questions", json=new_questions)
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_winners():
    response = client.get("/campaigns/all")
    campaign_id = response.json()["items"][0]["id"]

    # Assign winner
    winner_payload = {
        "participantName": "John Doe",
        "prize": "Gold Trophy",
        "winnerType": "Final"
    }
    response = client.post(f"/campaigns/{campaign_id}/winners", json=winner_payload)
    assert response.status_code == 200
    winner_data = response.json()
    assert winner_data["participantName"] == "John Doe"
    winner_id = winner_data["id"]

    # Get winners
    response = client.get(f"/campaigns/{campaign_id}/winners")
    assert response.status_code == 200
    assert len(response.json()) == 1

    # Delete winner
    response = client.delete(f"/campaigns/{campaign_id}/winners/{winner_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Winner removed successfully"

def test_communications():
    response = client.get("/campaigns/all")
    campaign_id = response.json()["items"][0]["id"]

    comm_payload = {
        "channel": "email",
        "recipientType": "all",
        "subject": "Hello Participants",
        "message": "This is a test message",
        "sentBy": "Admin"
    }
    response = client.post(f"/campaigns/{campaign_id}/communicate", json=comm_payload)
    assert response.status_code == 200
    assert response.json()["channel"] == "email"

    response = client.get(f"/campaigns/{campaign_id}/communications")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_date_validation():
    payload = {
        "name": "Invalid Dates Campaign",
        "startDate": "2024-12-31T23:59:59",
        "endDate": "2024-01-01T00:00:00"
    }
    response = client.post("/campaigns/create", json=payload)
    assert response.status_code == 422

def test_bulk_create():
    payload = [
        {"name": "Bulk 1"},
        {"name": "Bulk 2"}
    ]
    response = client.post("/campaigns/bulk-create", json=payload)
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["slug"] == "bulk-1"

def test_submission_count():
    # Create campaign
    response = client.post("/campaigns/create", json={"name": "Sub Test"})
    campaign_id = response.json()["id"]

    # Add participant
    response = client.post(f"/campaigns/{campaign_id}/participants", json={"participantName": "Tester"})
    assert response.status_code == 200
    participant_id = response.json()["id"]

    # Verify participant count
    response = client.get(f"/campaigns/{campaign_id}")
    assert response.json()["totalParticipants"] == 1
    assert response.json()["totalSubmissions"] == 0

    # Submit entry
    response = client.post(f"/campaigns/{campaign_id}/submit", json={"participantId": participant_id})
    assert response.status_code == 200

    # Verify submission count
    response = client.get(f"/campaigns/{campaign_id}")
    assert response.json()["totalSubmissions"] == 1

    # Remove participant and verify counts
    response = client.delete(f"/campaigns/{campaign_id}/participants/{participant_id}")
    assert response.status_code == 200

    response = client.get(f"/campaigns/{campaign_id}")
    assert response.json()["totalParticipants"] == 0
    assert response.json()["totalSubmissions"] == 0
