"""
Edix - Universal Data Structure Editor
Main FastAPI application
"""
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

from .database import DatabaseManager
from .schemas import SchemaManager
from .models import Structure, DataItem, Schema
from .api.v1 import api_router
from .api.websocket import websocket_endpoint


# Get package directory
PACKAGE_DIR = Path(__file__).parent
STATIC_DIR = PACKAGE_DIR / "static"
TEMPLATES_DIR = PACKAGE_DIR / "templates"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🚀 Starting Edix server...")
    app.state.db = DatabaseManager()
    await app.state.db.initialize()
    app.state.schema_manager = SchemaManager(app.state.db)
    await app.state.schema_manager.load_schemas()
    
    yield
    
    # Shutdown
    print("🔌 Shutting down Edix server...")
    await app.state.db.close()


# Create FastAPI app
app = FastAPI(
    title="Edix",
    description="Universal Data Structure Editor",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Setup templates
try:
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
except Exception as e:
    print(f"⚠️ Templates not found at {TEMPLATES_DIR}. UI will not be available.")
    templates = None

# Include API routes
app.include_router(api_router, prefix="/api")

# WebSocket for real-time updates
app.add_api_websocket_route("/ws", websocket_endpoint)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Main editor interface"""
    if not templates:
        raise HTTPException(status_code=500, detail="Templates not found. UI is not available.")
    return templates.TemplateResponse(
        "editor.html",
        {"request": request, "title": "Edix Editor"}
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/api/structures")
async def list_structures(request: Request):
    """List all available data structures"""
    db = request.app.state.db
    structures = await db.list_structures()
    return structures


@app.post("/api/structures")
async def create_structure(request: Request, structure: Structure):
    """Create a new data structure with dynamic SQL table"""
    db = request.app.state.db
    schema_manager = request.app.state.schema_manager
    
    try:
        # Validate schema
        await schema_manager.validate_schema(structure.schema)
        
        # Create SQL table based on schema
        await db.create_table_from_schema(
            structure.name,
            structure.schema
        )
        
        # Save structure definition
        await db.save_structure(structure)
        
        return {
            "status": "success",
            "message": f"Structure '{structure.name}' created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/structures/{structure_name}/data")
async def get_structure_data(request: Request, structure_name: str):
    """Get all data for a structure"""
    db = request.app.state.db
    
    try:
        data = await db.get_structure_data(structure_name)
        return data
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/structures/{structure_name}/data")
async def insert_structure_data(
    request: Request,
    structure_name: str,
    data: Dict[str, Any]
):
    """Insert data into a structure"""
    db = request.app.state.db
    schema_manager = request.app.state.schema_manager
    
    try:
        # Validate data against schema
        schema = await db.get_structure_schema(structure_name)
        await schema_manager.validate_data(data, schema)
        
        # Insert data
        result = await db.insert_data(structure_name, data)
        
        return {
            "status": "success",
            "id": result["id"],
            "message": "Data inserted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/api/structures/{structure_name}/data/{item_id}")
async def update_structure_data(
    request: Request,
    structure_name: str,
    item_id: int,
    data: Dict[str, Any]
):
    """Update data in a structure"""
    db = request.app.state.db
    schema_manager = request.app.state.schema_manager
    
    try:
        # Validate data against schema
        schema = await db.get_structure_schema(structure_name)
        await schema_manager.validate_data(data, schema)
        
        # Update data
        await db.update_data(structure_name, item_id, data)
        
        return {
            "status": "success",
            "message": "Data updated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/structures/{structure_name}/data/{item_id}")
async def delete_structure_data(
    request: Request,
    structure_name: str,
    item_id: int
):
    """Delete data from a structure"""
    db = request.app.state.db
    
    try:
        await db.delete_data(structure_name, item_id)
        return {
            "status": "success",
            "message": "Data deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/export/{format}")
async def export_data(
    request: Request,
    format: str,
    structure_name: Optional[str] = None
):
    """Export data in various formats"""
    db = request.app.state.db
    
    if format not in ["json", "yaml", "csv", "xml", "excel"]:
        raise HTTPException(status_code=400, detail="Unsupported format")
    
    try:
        if structure_name:
            data = await db.export_structure(structure_name, format)
        else:
            data = await db.export_all(format)
        
        return {
            "status": "success",
            "format": format,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/import/{format}")
async def import_data(
    request: Request,
    format: str,
    data: Dict[str, Any]
):
    """Import data from various formats"""
    db = request.app.state.db
    
    if format not in ["json", "yaml", "csv", "xml", "excel"]:
        raise HTTPException(status_code=400, detail="Unsupported format")
    
    try:
        result = await db.import_data(format, data)
        return {
            "status": "success",
            "imported": result["count"],
            "message": f"Imported {result['count']} records"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/embed/{structure_name}")
async def embed_editor(request: Request, structure_name: str):
    """Embeddable editor for integration with existing websites"""
    if not templates:
        raise HTTPException(status_code=500, detail="Templates not found. UI is not available.")
    return templates.TemplateResponse(
        "embed.html",
        {
            "request": request,
            "structure_name": structure_name,
            "embed_mode": True
        }
    )


def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False
):
    """Run the Edix server"""
    import uvicorn
    
    print(f"🌐 Starting Edix server at http://{host}:{port}")
    print("Press Ctrl+C to stop")
    
    uvicorn.run(
        "edix.app:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    run_server(reload=True)
