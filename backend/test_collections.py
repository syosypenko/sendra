import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from bson import ObjectId
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app
from src.database import db

client = TestClient(app)

# Mock user for testing
MOCK_USER = {
    "_id": ObjectId(),
    "email": "test@example.com",
    "google_id": "google_123",
    "name": "Test User"
}

MOCK_EMAIL = {
    "gmail_id": "msg_123",
    "subject": "Test Email",
    "from": "sender@example.com",
    "to": ["test@example.com"],
    "body": "This is a test email body",
    # Gmail returns RFC2822 style strings; allow them without strict parsing
    "received_at": "Fri, 26 Dec 2025 18:27:03 +0000 (UTC)"
}


@pytest.fixture
def mock_get_current_user(monkeypatch):
    """Mock get_current_user dependency"""
    async def mock_user():
        return MOCK_USER
    
    from src import dependencies
    monkeypatch.setattr(dependencies, "get_current_user", mock_user)
    return mock_user


@pytest.fixture
async def mock_db(monkeypatch):
    """Mock database operations"""
    mock_db = AsyncMock()
    mock_collection = AsyncMock()
    
    mock_db.get_db.return_value.collections = mock_collection
    
    monkeypatch.setattr("src.routes.collection_routes.db", mock_db)
    return mock_db


@pytest.mark.asyncio
async def test_create_collection(mock_get_current_user, mock_db):
    """Test POST /collections to create a new collection"""
    payload = {
        "name": "Test Collection",
        "emails": [MOCK_EMAIL]
    }
    
    # Mock insert response
    mock_db.get_db.return_value.collections.insert_one = AsyncMock(
        return_value=MagicMock(inserted_id=ObjectId())
    )
    mock_db.get_db.return_value.collections.find_one = AsyncMock(
        return_value={
            "_id": ObjectId(),
            "user_id": MOCK_USER["_id"],
            "name": "Test Collection",
            "emails": [MOCK_EMAIL],
            "created_at": datetime.utcnow().isoformat()
        }
    )
    
    response = client.post("/collections/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Collection"
    assert len(data["emails"]) == 1


@pytest.mark.asyncio
async def test_create_collection_missing_name(mock_get_current_user):
    """Test POST /collections without name returns 400"""
    payload = {
        "emails": [MOCK_EMAIL]
    }
    
    response = client.post("/collections/", json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_collection_no_emails(mock_get_current_user):
    """Test POST /collections without emails returns 400"""
    payload = {
        "name": "Empty Collection"
    }
    
    response = client.post("/collections/", json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_list_collections(mock_get_current_user, mock_db):
    """Test GET /collections to list user's collections"""
    mock_collections = [
        {
            "_id": ObjectId(),
            "user_id": MOCK_USER["_id"],
            "name": "Collection 1",
            "emails": [MOCK_EMAIL],
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "_id": ObjectId(),
            "user_id": MOCK_USER["_id"],
            "name": "Collection 2",
            "emails": [],
            "created_at": datetime.utcnow().isoformat()
        }
    ]
    
    mock_cursor = AsyncMock()
    mock_cursor.to_list = AsyncMock(return_value=mock_collections)
    mock_db.get_db.return_value.collections.find.return_value.sort.return_value = mock_cursor
    
    response = client.get("/collections/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Collection 1"


@pytest.mark.asyncio
async def test_get_collection(mock_get_current_user, mock_db):
    """Test GET /collections/{id} to retrieve single collection"""
    collection_id = ObjectId()
    mock_collection_data = {
        "_id": collection_id,
        "user_id": MOCK_USER["_id"],
        "name": "Test Collection",
        "emails": [MOCK_EMAIL],
        "created_at": datetime.utcnow().isoformat()
    }
    
    mock_db.get_db.return_value.collections.find_one = AsyncMock(
        return_value=mock_collection_data
    )
    
    response = client.get(f"/collections/{str(collection_id)}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Collection"
    assert len(data["emails"]) == 1


@pytest.mark.asyncio
async def test_get_collection_not_found(mock_get_current_user, mock_db):
    """Test GET /collections/{id} with invalid ID returns 404"""
    mock_db.get_db.return_value.collections.find_one = AsyncMock(return_value=None)
    
    response = client.get(f"/collections/{str(ObjectId())}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_collection_invalid_id(mock_get_current_user):
    """Test GET /collections/{id} with invalid ObjectId format returns 404"""
    response = client.get("/collections/invalid_id")
    assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
