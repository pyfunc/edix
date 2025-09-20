# requirements.txt
"""
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
pydantic>=2.0.0
pyyaml>=6.0
aiosqlite>=0.19.0
jinja2>=3.1.0
python-multipart>=0.0.6
websockets>=11.0
jsonschema>=4.19.0
alembic>=1.12.0
"""

# tests/test_edix.py
"""
Basic tests for Edix
"""
import pytest
import asyncio
import json
from pathlib import Path
import tempfile
from fastapi.testclient import TestClient

from edix.app import app
from edix.database import DatabaseManager
from edix.schemas import SchemaManager
from edix.models import Structure, Schema


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
async def db():
    """Create test database"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    db = DatabaseManager(db_path)
    await db.initialize()
    yield db
    await db.close()
    
    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_database_initialization(db):
    """Test database initialization"""
    assert db.connection is not None
    
    # Check if system tables exist
    cursor = await db.connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )
    tables = await cursor.fetchall()
    table_names = [t[0] for t in tables]
    
    assert "edix_structures" in table_names
    assert "edix_migrations" in table_names


@pytest.mark.asyncio
async def test_create_structure(db):
    """Test creating a data structure"""
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"}
        },
        "required": ["name"]
    }
    
    await db.create_table_from_schema("test_structure", schema)
    
    # Check if table was created
    cursor = await db.connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'edix_data_%'"
    )
    tables = await cursor.fetchall()
    
    assert len(tables) > 0
    assert "edix_data_test_structure" in tables[0][0]


@pytest.mark.asyncio
async def test_insert_and_retrieve_data(db):
    """Test inserting and retrieving data"""
    # Create structure
    schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "count": {"type": "integer"}
        }
    }
    
    await db.create_table_from_schema("items", schema)
    
    # Insert data
    test_data = {
        "title": "Test Item",
        "count": 42
    }
    
    result = await db.insert_data("items", test_data)
    assert "id" in result
    
    # Retrieve data
    data = await db.get_structure_data("items")
    assert len(data) == 1
    assert data[0]["title"] == "Test Item"
    assert data[0]["count"] == 42


def test_api_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_api_root_page(client):
    """Test root page returns HTML"""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_schema_validation():
    """Test schema validation"""
    db = DatabaseManager(":memory:")
    await db.initialize()
    
    schema_manager = SchemaManager(db)
    
    # Valid schema
    valid_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"}
        }
    }
    
    result = await schema_manager.validate_schema(valid_schema)
    assert result is True
    
    # Invalid schema
    invalid_schema = {
        "type": "invalid_type",
        "properties": {}
    }
    
    with pytest.raises(ValueError):
        await schema_manager.validate_schema(invalid_schema)
    
    await db.close()


@pytest.mark.asyncio
async def test_export_import(db):
    """Test data export and import"""
    # Create structure and add data
    schema = {
        "type": "object",
        "properties": {
            "key": {"type": "string"},
            "value": {"type": "string"}
        }
    }
    
    await db.create_table_from_schema("config", schema)
    
    # Insert test data
    test_data = [
        {"key": "setting1", "value": "value1"},
        {"key": "setting2", "value": "value2"}
    ]
    
    for item in test_data:
        await db.insert_data("config", item)
    
    # Export as JSON
    exported = await db.export_structure("config", "json")
    assert len(exported) == 2
    
    # Export as YAML
    yaml_export = await db.export_structure("config", "yaml")
    assert "setting1" in yaml_export
    assert "value1" in yaml_export


@pytest.mark.asyncio
async def test_update_delete_data(db):
    """Test updating and deleting data"""
    # Create structure
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "status": {"type": "string"}
        }
    }
    
    await db.create_table_from_schema("tasks", schema)
    
    # Insert data
    data = {"name": "Task 1", "status": "pending"}
    result = await db.insert_data("tasks", data)
    task_id = result["id"]
    
    # Update data
    await db.update_data("tasks", task_id, {"status": "completed"})
    
    # Verify update
    tasks = await db.get_structure_data("tasks")
    assert tasks[0]["status"] == "completed"
    
    # Delete data
    await db.delete_data("tasks", task_id)
    
    # Verify deletion
    tasks = await db.get_structure_data("tasks")
    assert len(tasks) == 0


@pytest.mark.parametrize("json_type,sql_type", [
    ("string", "TEXT"),
    ("integer", "INTEGER"),
    ("number", "REAL"),
    ("boolean", "INTEGER"),
    ("array", "JSON"),
    ("object", "JSON"),
])
def test_type_mapping(json_type, sql_type):
    """Test JSON to SQL type mapping"""
    db = DatabaseManager(":memory:")
    result = db._get_sql_type(json_type)
    assert result == sql_type


# tests/conftest.py
"""
Pytest configuration
"""
import pytest
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# tests/__init__.py
"""Tests package"""


# .gitignore
"""
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
ENV/
env/
edix_env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log

# Frontend
node_modules/
frontend_src/node_modules/
edix/static/app.js
edix/static/*.map

# Testing
.coverage
.pytest_cache/
.mypy_cache/
.ruff_cache/
htmlcov/
.tox/

# Config
edix.yaml
config.yaml
.env

# Docker
.dockerignore
"""

# .dockerignore
"""
# Git
.git
.gitignore

# Python
__pycache__
*.pyc
*.pyo
*.pyd
.Python
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Virtual environments
venv/
ENV/
env/

# IDEs
.vscode/
.idea/

# Frontend source (we only need built files)
frontend_src/node_modules/

# Documentation
docs/
*.md

# Tests
tests/
test_*.py

# Development files
Makefile
setup.cfg
.editorconfig
"""