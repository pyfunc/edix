"""Tests for database functionality."""
import pytest
import asyncio
import json
import tempfile
import os
from pathlib import Path

from edix.database import DatabaseManager


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
            "age": {"type": "integer", "minimum": 0},
            "active": {"type": "boolean"},
            "tags": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["id", "name", "email"]
    }


@pytest.fixture
def sample_data():
    """Sample data for testing."""
    return [
        {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "age": 30,
            "active": True,
            "tags": ["developer", "python"]
        },
        {
            "id": 2,
            "name": "Jane Smith",
            "email": "jane@example.com",
            "age": 25,
            "active": False,
            "tags": ["designer", "ui"]
        }
    ]


@pytest.mark.asyncio
async def test_database_initialization(temp_db):
    """Test database initialization."""
    await temp_db.initialize()
    assert temp_db.db_path.exists()


@pytest.mark.asyncio
async def test_create_table_from_schema(temp_db, sample_schema):
    """Test creating table from JSON schema."""
    await temp_db.initialize()
    
    table_name = "users"
    await temp_db.create_table_from_schema(table_name, sample_schema)
    
    tables = await temp_db.list_tables()
    assert table_name in tables


@pytest.mark.asyncio
async def test_insert_data(temp_db, sample_schema, sample_data):
    """Test inserting data into table."""
    await temp_db.initialize()
    
    table_name = "users"
    await temp_db.create_table_from_schema(table_name, sample_schema)
    
    for item in sample_data:
        await temp_db.insert_item(table_name, item)
    
    items = await temp_db.get_all_items(table_name)
    assert len(items) == 2
    assert items[0]["name"] == "John Doe"
    assert items[1]["name"] == "Jane Smith"


@pytest.mark.asyncio
async def test_update_data(temp_db, sample_schema, sample_data):
    """Test updating data in table."""
    await temp_db.initialize()
    
    table_name = "users"
    await temp_db.create_table_from_schema(table_name, sample_schema)
    
    # Insert first item
    await temp_db.insert_item(table_name, sample_data[0])
    
    # Update it
    updated_data = sample_data[0].copy()
    updated_data["age"] = 35
    await temp_db.update_item(table_name, 1, updated_data)
    
    items = await temp_db.get_all_items(table_name)
    assert items[0]["age"] == 35


@pytest.mark.asyncio
async def test_delete_data(temp_db, sample_schema, sample_data):
    """Test deleting data from table."""
    await temp_db.initialize()
    
    table_name = "users"
    await temp_db.create_table_from_schema(table_name, sample_schema)
    
    # Insert items
    for item in sample_data:
        await temp_db.insert_item(table_name, item)
    
    # Delete first item
    await temp_db.delete_item(table_name, 1)
    
    items = await temp_db.get_all_items(table_name)
    assert len(items) == 1
    assert items[0]["id"] == 2


@pytest.mark.asyncio
async def test_export_data(temp_db, sample_schema, sample_data):
    """Test exporting data to JSON."""
    await temp_db.initialize()
    
    table_name = "users"
    await temp_db.create_table_from_schema(table_name, sample_schema)
    
    # Insert data
    for item in sample_data:
        await temp_db.insert_item(table_name, item)
    
    # Export data
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        export_path = f.name
    
    try:
        await temp_db.export_data(table_name, export_path, 'json')
        
        # Verify exported data
        with open(export_path, 'r') as f:
            exported_data = json.load(f)
        
        assert len(exported_data) == 2
        assert exported_data[0]["name"] == "John Doe"
    finally:
        if os.path.exists(export_path):
            os.unlink(export_path)


@pytest.mark.asyncio
async def test_import_data(temp_db, sample_schema):
    """Test importing data from JSON."""
    await temp_db.initialize()
    
    table_name = "users"
    await temp_db.create_table_from_schema(table_name, sample_schema)
    
    # Create test data file
    test_data = [
        {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 28},
        {"id": 2, "name": "Bob", "email": "bob@example.com", "age": 32}
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        import_path = f.name
    
    try:
        await temp_db.import_data(table_name, import_path, 'json')
        
        items = await temp_db.get_all_items(table_name)
        assert len(items) == 2
        assert items[0]["name"] == "Alice"
        assert items[1]["name"] == "Bob"
    finally:
        if os.path.exists(import_path):
            os.unlink(import_path)


@pytest.mark.asyncio
async def test_schema_validation(temp_db):
    """Test schema validation."""
    await temp_db.initialize()
    
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string", "minLength": 1}
        },
        "required": ["id", "name"]
    }
    
    table_name = "test_table"
    await temp_db.create_table_from_schema(table_name, schema)
    
    # Valid data should work
    valid_data = {"id": 1, "name": "Test"}
    await temp_db.insert_item(table_name, valid_data)
    
    # Invalid data should raise an error
    invalid_data = {"id": "not_an_int", "name": ""}
    with pytest.raises(Exception):
        await temp_db.insert_item(table_name, invalid_data)


@pytest.mark.asyncio
async def test_list_tables(temp_db, sample_schema):
    """Test listing tables."""
    await temp_db.initialize()
    
    # Initially should have no tables (except system tables)
    initial_tables = await temp_db.list_tables()
    
    # Create a table
    await temp_db.create_table_from_schema("test_table", sample_schema)
    
    tables = await temp_db.list_tables()
    assert "test_table" in tables
    assert len(tables) >= len(initial_tables) + 1


@pytest.mark.asyncio
async def test_get_schema(temp_db, sample_schema):
    """Test getting table schema."""
    await temp_db.initialize()
    
    table_name = "users"
    await temp_db.create_table_from_schema(table_name, sample_schema)
    
    retrieved_schema = await temp_db.get_schema(table_name)
    assert retrieved_schema is not None
    assert retrieved_schema["type"] == "object"
    assert "properties" in retrieved_schema


if __name__ == "__main__":
    pytest.main([__file__])
