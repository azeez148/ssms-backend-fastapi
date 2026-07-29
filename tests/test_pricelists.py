import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from app.main import app
from app.core.database import Base, get_db
from app.models.category import Category

# Setup the test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_api.db"
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
    db = TestingSessionLocal()
    # Add a test category
    cat = Category(name="Test Category", description="Test Description")
    db.add(cat)
    db.commit()
    db.refresh(cat)
    yield cat
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_api.db"):
        os.remove("./test_api.db")

client = TestClient(app)

def test_pricelist_crud(setup_db):
    category = setup_db

    # 1. Create
    response = client.post(
        "/pricelists/",
        json={
            "category_id": category.id,
            "unit_price": 100,
            "selling_price": 150,
            "discounted_price": 120
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["category_id"] == category.id
    assert data["unit_price"] == 100
    pricelist_id = data["id"]

    # 2. Get all
    response = client.get("/pricelists/")
    assert response.status_code == 200
    assert len(response.json()) >= 1

    # 3. Get by ID
    response = client.get(f"/pricelists/{pricelist_id}")
    assert response.status_code == 200
    assert response.json()["id"] == pricelist_id

    # 4. Get by Category ID
    response = client.get(f"/pricelists/category/{category.id}")
    assert response.status_code == 200
    assert response.json()["id"] == pricelist_id

    # 5. Update
    response = client.put(
        f"/pricelists/{pricelist_id}",
        json={"selling_price": 160}
    )
    assert response.status_code == 200
    assert response.json()["selling_price"] == 160

    # 6. Delete
    response = client.delete(f"/pricelists/{pricelist_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Pricelist deleted successfully"

    # 7. Verify deletion
    response = client.get(f"/pricelists/{pricelist_id}")
    assert response.status_code == 404
