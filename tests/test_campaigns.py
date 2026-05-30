import pytest
from starlette.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app


# Use SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_campaigns.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Create tables
Base.metadata.create_all(bind=engine)

client = TestClient(app)


class TestCampaignCRUD:
    def test_create_campaign(self):
        payload = {
            "name": "Summer Giveaway",
            "slug": "summer-giveaway",
            "description": "Win prizes this summer!",
            "campaign_type": "giveaway",
            "status": "draft",
            "terms_and_conditions": "Must be 18+",
            "metadata_json": {"theme": "summer", "color": "#FFD700"},
            "participation_requirements": {"email_required": True},
            "is_active": True,
            "media": [
                {"media_type": "image", "url": "https://example.com/banner.png", "title": "Banner"}
            ],
            "forms": [
                {
                    "name": "Entry Form",
                    "description": "Fill to enter",
                    "is_required": True,
                    "sort_order": 0,
                    "fields": [
                        {
                            "field_name": "favorite_color",
                            "field_label": "What is your favorite color?",
                            "field_type": "text",
                            "is_required": True,
                            "sort_order": 0,
                        },
                        {
                            "field_name": "age_group",
                            "field_label": "Age Group",
                            "field_type": "select",
                            "is_required": True,
                            "options": ["18-25", "26-35", "36-45", "46+"],
                            "sort_order": 1,
                        },
                    ],
                }
            ],
            "deadlines": [
                {
                    "deadline_type": "registration",
                    "ends_at": "2027-12-31T23:59:59Z",
                    "is_enforced": True,
                },
                {
                    "deadline_type": "submission",
                    "ends_at": "2027-12-31T23:59:59Z",
                    "is_enforced": True,
                },
            ],
            "winner_configs": [
                {"strategy": "random", "max_winners": 3, "is_active": True}
            ],
            "communications": [
                {
                    "channel": "email",
                    "trigger": "registration",
                    "template_subject": "Welcome!",
                    "template_body": "Thank you for registering for {{campaign_name}}!",
                    "is_active": True,
                }
            ],
        }
        response = client.post("/campaigns/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Summer Giveaway"
        assert data["slug"] == "summer-giveaway"
        assert len(data["media"]) == 1
        assert len(data["forms"]) == 1
        assert len(data["forms"][0]["fields"]) == 2
        assert len(data["deadlines"]) == 2
        assert len(data["winner_configs"]) == 1
        assert len(data["communications"]) == 1

    def test_list_campaigns(self):
        response = client.get("/campaigns/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_get_campaign_by_slug(self):
        response = client.get("/campaigns/slug/summer-giveaway")
        assert response.status_code == 200
        assert response.json()["slug"] == "summer-giveaway"

    def test_update_campaign(self):
        response = client.put("/campaigns/1", json={"status": "active"})
        assert response.status_code == 200
        assert response.json()["status"] == "active"

    def test_list_active_campaigns(self):
        response = client.get("/campaigns/active")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all(c["status"] == "active" for c in data)


class TestCampaignParticipation:
    def test_register_participant(self):
        payload = {
            "name": "John Doe",
            "email": "john@example.com",
            "whatsapp_number": "+1234567890",
        }
        response = client.post("/campaigns/1/participants", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "John Doe"
        assert data["status"] == "registered"

    def test_register_participant_without_required_email(self):
        # Campaign requires email
        payload = {"name": "No Email User"}
        response = client.post("/campaigns/1/participants", json=payload)
        assert response.status_code == 400

    def test_list_participants(self):
        response = client.get("/campaigns/1/participants")
        assert response.status_code == 200
        assert len(response.json()) >= 1


class TestCampaignSubmissions:
    def test_submit_response(self):
        payload = {
            "form_id": 1,
            "response_data": {"favorite_color": "blue", "age_group": "26-35"},
        }
        response = client.post("/campaigns/1/participants/1/submissions", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["response_data"]["favorite_color"] == "blue"

    def test_get_submissions(self):
        response = client.get("/campaigns/participants/1/submissions")
        assert response.status_code == 200
        assert len(response.json()) >= 1


class TestCampaignResults:
    def test_select_winners(self):
        response = client.post("/campaigns/1/winners", json=[1])
        assert response.status_code == 200
        assert response.json()["message"] == "1 winner(s) selected"

    def test_get_results(self):
        response = client.get("/campaigns/1/results")
        assert response.status_code == 200
        data = response.json()
        assert data["campaign_id"] == 1
        assert data["total_participants"] >= 1
        assert data["total_submissions"] >= 1
        assert len(data["winners"]) >= 1


class TestCampaignNotFound:
    def test_get_nonexistent(self):
        response = client.get("/campaigns/999")
        assert response.status_code == 404

    def test_delete_campaign(self):
        # Create one to delete
        payload = {
            "name": "Temp Campaign",
            "slug": "temp-campaign",
            "campaign_type": "contest",
            "status": "draft",
            "is_active": True,
        }
        resp = client.post("/campaigns/", json=payload)
        cid = resp.json()["id"]
        response = client.delete(f"/campaigns/{cid}")
        assert response.status_code == 200
        # Verify deleted
        response = client.get(f"/campaigns/{cid}")
        assert response.status_code == 404
