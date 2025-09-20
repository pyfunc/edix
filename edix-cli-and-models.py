# edix/__init__.py
"""
Edix - Universal Data Structure Editor
"""
__version__ = "1.0.0"
__author__ = "Your Name"

from .app import app, run_server
from .database import DatabaseManager
from .schemas import SchemaManager

__all__ = ["app", "run_server", "DatabaseManager", "SchemaManager"]


# edix/__main__.py
"""
CLI entry point for Edix
"""
import argparse
import sys
from pathlib import Path
from .app import run_server


def main():
    parser = argparse.ArgumentParser(description="Edix - Universal Data Structure Editor")
    parser.add_argument(
        "command",
        choices=["serve", "init", "migrate", "export", "import"],
        help="Command to execute"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Server host")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--db", default="edix.db", help="Database file")
    parser.add_argument("--format", choices=["json", "yaml", "csv", "xml"], help="Export format")
    parser.add_argument("--file", help="Import/export file")
    parser.add_argument("--structure", help="Structure name")
    
    args = parser.parse_args()
    
    if args.command == "serve":
        print(f"🚀 Starting Edix server on http://{args.host}:{args.port}")
        print(f"📁 Database: {args.db}")
        print("\nPress Ctrl+C to stop\n")
        run_server(host=args.host, port=args.port)
        
    elif args.command == "init":
        from .database import DatabaseManager
        import asyncio
        
        async def init_db():
            db = DatabaseManager(args.db)
            await db.initialize()
            print(f"✅ Database initialized: {args.db}")
            await db.close()
        
        asyncio.run(init_db())
        
    elif args.command == "export":
        if not args.format or not args.file:
            print("Error: --format and --file are required for export")
            sys.exit(1)
            
        # Export logic here
        print(f"Exporting to {args.file} in {args.format} format...")
        
    elif args.command == "import":
        if not args.format or not args.file:
            print("Error: --format and --file are required for import")
            sys.exit(1)
            
        # Import logic here
        print(f"Importing from {args.file} ({args.format} format)...")
    
    elif args.command == "migrate":
        print("Running database migrations...")
        # Migration logic here


if __name__ == "__main__":
    main()


# edix/models.py
"""
Pydantic models for validation
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class Schema(BaseModel):
    """JSON Schema definition"""
    type: str = "object"
    properties: Dict[str, Any] = Field(default_factory=dict)
    required: List[str] = Field(default_factory=list)
    additionalProperties: bool = False
    
    @validator("type")
    def validate_type(cls, v):
        valid_types = ["object", "array", "string", "number", "integer", "boolean", "null"]
        if v not in valid_types:
            raise ValueError(f"Invalid type: {v}")
        return v


class Structure(BaseModel):
    """Data structure definition"""
    name: str
    schema: Dict[str, Any]
    meta: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @validator("name")
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Structure name cannot be empty")
        # Sanitize name
        import re
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", v):
            raise ValueError("Invalid structure name. Use only letters, numbers, underscore, and hyphen.")
        return v


class DataItem(BaseModel):
    """Generic data item"""
    id: Optional[int] = None
    data: Dict[str, Any]
    meta: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ExportRequest(BaseModel):
    """Export request model"""
    format: str = Field(..., regex="^(json|yaml|csv|xml|excel)$")
    structure_name: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None


class ImportRequest(BaseModel):
    """Import request model"""
    format: str = Field(..., regex="^(json|yaml|csv|xml|excel)$")
    data: Any
    structure_name: Optional[str] = None
    options: Optional[Dict[str, Any]] = None


# edix/schemas.py
"""
Schema validation and management
"""
import json
from typing import Dict, Any, List
from jsonschema import validate, ValidationError, Draft7Validator


class SchemaManager:
    """Manage and validate schemas"""
    
    def __init__(self, database_manager):
        self.db = database_manager
        self.schemas = {}
        
    async def load_schemas(self):
        """Load all schemas from database"""
        structures = await self.db.list_structures()
        for structure in structures:
            self.schemas[structure["name"]] = structure["schema"]
    
    async def validate_schema(self, schema: Dict[str, Any]):
        """Validate a JSON schema"""
        try:
            # Check if it's a valid JSON Schema
            Draft7Validator.check_schema(schema)
            return True
        except Exception as e:
            raise ValueError(f"Invalid schema: {str(e)}")
    
    async def validate_data(self, data: Dict[str, Any], schema: Dict[str, Any]):
        """Validate data against schema"""
        try:
            validate(instance=data, schema=schema)
            return True
        except ValidationError as e:
            raise ValueError(f"Data validation failed: {e.message}")
    
    def generate_form_schema(self, json_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate form schema from JSON schema for UI"""
        form_schema = {
            "fields": [],
            "required": json_schema.get("required", [])
        }
        
        properties = json_schema.get("properties", {})
        
        for prop_name, prop_schema in properties.items():
            field = {
                "name": prop_name,
                "type": self._map_type_to_input(prop_schema.get("type", "string")),
                "label": prop_schema.get("title", prop_name),
                "description": prop_schema.get("description", ""),
                "required": prop_name in json_schema.get("required", []),
                "validation": {}
            }
            
            # Add validation rules
            if "minLength" in prop_schema:
                field["validation"]["minLength"] = prop_schema["minLength"]
            if "maxLength" in prop_schema:
                field["validation"]["maxLength"] = prop_schema["maxLength"]
            if "minimum" in prop_schema:
                field["validation"]["min"] = prop_schema["minimum"]
            if "maximum" in prop_schema:
                field["validation"]["max"] = prop_schema["maximum"]
            if "enum" in prop_schema:
                field["type"] = "select"
                field["options"] = prop_schema["enum"]
            if "pattern" in prop_schema:
                field["validation"]["pattern"] = prop_schema["pattern"]
            
            form_schema["fields"].append(field)
        
        return form_schema
    
    def _map_type_to_input(self, json_type: str) -> str:
        """Map JSON schema type to HTML input type"""
        type_map = {
            "string": "text",
            "number": "number",
            "integer": "number",
            "boolean": "checkbox",
            "array": "array",
            "object": "object"
        }
        return type_map.get(json_type, "text")


# edix/api/__init__.py
"""API module"""
from .routes import router

__all__ = ["router"]


# edix/api/routes.py
"""API routes"""
from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any, List

router = APIRouter()


@router.get("/schema/{structure_name}")
async def get_schema(request: Request, structure_name: str):
    """Get schema for a structure"""
    db = request.app.state.db
    schema = await db.get_structure_schema(structure_name)
    return schema


@router.put("/schema/{structure_name}")
async def update_schema(request: Request, structure_name: str, schema: Dict[str, Any]):
    """Update schema for a structure"""
    # This would need migration logic
    return {"status": "success", "message": "Schema updated"}


@router.get("/form-schema/{structure_name}")
async def get_form_schema(request: Request, structure_name: str):
    """Get form schema for UI generation"""
    db = request.app.state.db
    schema_manager = request.app.state.schema_manager
    
    json_schema = await db.get_structure_schema(structure_name)
    form_schema = schema_manager.generate_form_schema(json_schema)
    
    return form_schema


# edix/api/websocket.py
"""WebSocket support for real-time updates"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import json


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            
            # Handle different message types
            if data.get("type") == "subscribe":
                structure = data.get("structure")
                # Subscribe to structure updates
                
            elif data.get("type") == "update":
                # Broadcast update to all connected clients
                await manager.broadcast({
                    "type": "data_update",
                    "structure": data.get("structure"),
                    "data": data.get("data")
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)