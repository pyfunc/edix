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

def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
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
