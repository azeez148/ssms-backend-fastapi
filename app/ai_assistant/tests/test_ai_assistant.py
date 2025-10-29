import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.ai_assistant.nlp_engine import NLPEngine
from app.ai_assistant.models import Intent

client = TestClient(app)

def test_nlp_engine_entity_extraction():
    engine = NLPEngine()
    
    # Test size extraction
    assert engine.extract_size("I want size L") == "L"
    assert engine.extract_size("UK 8") == "8"
    assert engine.extract_size("no size mentioned") is None
    
    # Test quantity extraction
    assert engine.extract_quantity("I need 2 pieces") == 2
    assert engine.extract_quantity("3 items please") == 3
    assert engine.extract_quantity("just one") == 1  # default

def test_chat_endpoint_authentication():
    response = client.post("/ai/chat", json={"message": "I need a jersey"})
    assert response.status_code == 401  # Unauthorized

@pytest.mark.asyncio
async def test_chat_endpoint_with_auth(authenticated_client):
    response = authenticated_client.post(
        "/ai/chat",
        json={"message": "I need a Manchester United jersey size L"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "success" in data
    
    # Check extracted info
    assert "extracted_info" in data
    if data["extracted_info"]:
        assert "product_name" in data["extracted_info"]
        assert "size" in data["extracted_info"]