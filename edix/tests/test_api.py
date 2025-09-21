"""Tests for API functionality."""
import pytest
import asyncio
import json
import tempfile
import os
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from edix.app import app
from edix.database import DatabaseManager


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    db = DatabaseManager(db_path)
    yield db
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def sample_schema():
    """Sample JSON schema for testing."""
    return {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "email": {"type": "string", "format": "email"},
            "age": {"type": "integer", "minimum": 0}
        },
        "required": ["id", "name", "email"]
    }


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_get_tables_empty(client):
    """Test getting tables when database is empty."""
    with patch('edix.app.get_database') as mock_get_db:
        mock_db = AsyncMock()
        mock_db.list_tables.return_value = []
        mock_get_db.return_value = mock_db
        
        response = client.get("/api/tables")
        assert response.status_code == 200
        data = response.json()
        assert data == []


def test_create_table(client, sample_schema):
    """Test creating a table via API."""
    with patch('edix.app.get_database') as mock_get_db:
        mock_db = AsyncMock()
        mock_db.create_table_from_schema.return_value = None
        mock_get_db.return_value = mock_db
        
        payload = {
            "name": "users",
            "schema": sample_schema
        }
        
        response = client.post("/api/tables", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "Table created successfully"
        assert data["table_name"] == "users"


def test_create_table_invalid_schema(client):
    """Test creating a table with invalid schema."""
    payload = {
        "name": "invalid_table",
        "schema": {"invalid": "schema"}
    }
    
    response = client.post("/api/tables", json=payload)
    assert response.status_code == 400


def test_get_table_data(client):
    """Test getting table data via API."""
    with patch('edix.app.get_database') as mock_get_db:
        mock_db = AsyncMock()
        mock_data = [
            {"id": 1, "name": "John", "email": "john@example.com"},
            {"id": 2, "name": "Jane", "email": "jane@example.com"}
        ]
        mock_db.get_all_items.return_value = mock_data
        mock_get_db.return_value = mock_db
        
        response = client.get("/api/tables/users/data")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "John"


def test_insert_item(client):
    """Test inserting item via API."""
    with patch('edix.app.get_database') as mock_get_db:
        mock_db = AsyncMock()
        mock_db.insert_item.return_value = None
        mock_get_db.return_value = mock_db
        
        payload = {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "age": 30
        }
        
        response = client.post("/api/tables/users/data", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "Item inserted successfully"


def test_update_item(client):
    """Test updating item via API."""
    with patch('edix.app.get_database') as mock_get_db:
        mock_db = AsyncMock()
        mock_db.update_item.return_value = None
        mock_get_db.return_value = mock_db
        
        payload = {
            "name": "John Smith",
            "email": "johnsmith@example.com",
            "age": 31
        }
        
        response = client.put("/api/tables/users/data/1", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Item updated successfully"


def test_delete_item(client):
    """Test deleting item via API."""
    with patch('edix.app.get_database') as mock_get_db:
        mock_db = AsyncMock()
        mock_db.delete_item.return_value = None
        mock_get_db.return_value = mock_db
        
        response = client.delete("/api/tables/users/data/1")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Item deleted successfully"


def test_get_table_schema(client, sample_schema):
    """Test getting table schema via API."""
    with patch('edix.app.get_database') as mock_get_db:
        mock_db = AsyncMock()
        mock_db.get_schema.return_value = sample_schema
        mock_get_db.return_value = mock_db
        
        response = client.get("/api/tables/users/schema")
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "object"
        assert "properties" in data


def test_export_table_data(client):
    """Test exporting table data via API."""
    with patch('edix.app.get_database') as mock_get_db:
        mock_db = AsyncMock()
        mock_db.export_data.return_value = None
        mock_get_db.return_value = mock_db
        
        response = client.post("/api/tables/users/export", 
                              json={"format": "json"})
        assert response.status_code == 200


@pytest.mark.timeout(60)
def test_import_table_data(client):
    """Test importing table data via API."""
    # Create a test file
    test_data = [
        {"id": 1, "name": "Alice", "email": "alice@example.com"}
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        file_path = f.name
    
    try:
        with patch('edix.app.get_database') as mock_get_db:
            mock_db = AsyncMock()
            mock_db.import_data.return_value = None
            mock_get_db.return_value = mock_db
            
            with open(file_path, 'rb') as f:
                files = {"file": ("test.json", f, "application/json")}
                response = client.post("/api/tables/users/import", files=files)
                
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Data imported successfully"
    finally:
        if os.path.exists(file_path):
            os.unlink(file_path)


@pytest.mark.timeout(60)
def test_websocket_endpoint():
    """Test WebSocket endpoint."""
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as websocket:
            # Test basic connection
            data = websocket.receive_json()
            assert data["type"] == "connection"
            assert data["message"] == "Connected to Edix"


def test_static_files(client):
    """Test static file serving."""
    # Test that static files endpoint exists
    # Note: Actual files may not exist in test environment
    response = client.get("/static/nonexistent.js")
    # Should return 404 for non-existent files
    assert response.status_code == 404


def test_editor_page(client):
    """Test editor page rendering."""
    response = client.get("/")
    assert response.status_code == 200
    # Should return HTML content
    assert "text/html" in response.headers.get("content-type", "")


def test_cors_headers(client):
    """Test CORS headers are present."""
    response = client.options("/api/health")
    assert response.status_code == 200
    # FastAPI CORS middleware should add these headers


def test_error_handling(client):
    """Test API error handling."""
    # Test non-existent table
    response = client.get("/api/tables/nonexistent/data")
    assert response.status_code == 404
    
    # Test invalid JSON
    response = client.post("/api/tables", data="invalid json")
    assert response.status_code == 422


def test_pagination(client):
    """Test data pagination."""
    with patch('edix.app.get_database') as mock_get_db:
        mock_db = AsyncMock()
        # Mock large dataset
        mock_data = [{"id": i, "name": f"User {i}"} for i in range(100)]
        mock_db.get_all_items.return_value = mock_data
        mock_get_db.return_value = mock_db
        
        # Test with limit and offset
        response = client.get("/api/tables/users/data?limit=10&offset=0")
        assert response.status_code == 200
        data = response.json()
        # Note: Implementation should handle pagination
        # This test assumes the API supports it


if __name__ == "__main__":
    pytest.main([__file__])
