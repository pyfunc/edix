""
Utility functions for file handling, including static files and templates.
"""
import os
import shutil
from pathlib import Path
from typing import Optional, Union

from fastapi import HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request

from .config import settings


def setup_static_files(app):
    """Set up static file serving for the FastAPI application."""
    # Create static directory if it doesn't exist
    os.makedirs(settings.STATIC_DIR, exist_ok=True)
    
    # Mount static files
    app.mount(
        "/static",
        StaticFiles(directory=settings.STATIC_DIR),
        name="static"
    )
    
    # Serve favicon.ico
    favicon_path = os.path.join(settings.STATIC_DIR, "favicon.ico")
    if os.path.exists(favicon_path):
        @app.get("/favicon.ico", include_in_schema=False)
        async def favicon():
            return FileResponse(favicon_path)


def get_template_path(template_name: str) -> Path:
    """Get the full path to a template file."""
    template_path = Path(settings.TEMPLATES_DIR) / template_name
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_name}")
    return template_path


def copy_static_files():
    """Copy static files from frontend build to static directory."""
    # Ensure static directory exists
    os.makedirs(settings.STATIC_DIR, exist_ok=True)
    
    # Copy files from frontend build to static directory
    frontend_build_dir = Path(settings.FRONTEND_DIR) / "build" / "static"
    
    if not frontend_build_dir.exists():
        raise FileNotFoundError(
            f"Frontend build directory not found at {frontend_build_dir}. "
            "Please build the frontend first."
        )
    
    # Copy all files from frontend build to static directory
    for item in frontend_build_dir.glob("**/*"):
        if item.is_file():
            rel_path = item.relative_to(frontend_build_dir)
            dest_path = Path(settings.STATIC_DIR) / rel_path
            os.makedirs(dest_path.parent, exist_ok=True)
            shutil.copy2(item, dest_path)


def get_asset_path(asset_name: str) -> str:
    """Get the URL path for a static asset."""
    return f"/static/{asset_name}"


def serve_react_app(request: Request) -> HTMLResponse:
    """Serve the main React application."""
    try:
        with open(Path(settings.TEMPLATES_DIR) / "editor.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content, status_code=200)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load the application: {str(e)}"
        )


def get_upload_path(filename: str, subfolder: str = "") -> Path:
    """Get the full path for an uploaded file."""
    upload_dir = Path(settings.UPLOAD_DIR)
    if subfolder:
        upload_dir = upload_dir / subfolder
    
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir / filename


def ensure_directory_exists(directory: Union[str, Path]):
    """Ensure that a directory exists, creating it if necessary."""
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_mime_type(filename: str) -> str:
    """Get the MIME type for a file based on its extension."""
    ext = Path(filename).suffix.lower()
    return {
        ".js": "application/javascript",
        ".css": "text/css",
        ".html": "text/html",
        ".json": "application/json",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".svg": "image/svg+xml",
        ".ico": "image/x-icon",
        ".woff": "font/woff",
        ".woff2": "font/woff2",
        ".ttf": "font/ttf",
        ".eot": "application/vnd.ms-fontobject",
    }.get(ext, "application/octet-stream")
