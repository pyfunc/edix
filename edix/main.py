""
Main FastAPI application for Edix - Universal Data Structure Editor.
"""
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import settings
from .database import DatabaseManager
from .routers import api_router
from .utils.files import setup_static_files, serve_react_app, copy_static_files

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT,
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Edix - Universal Data Structure Editor",
    version=settings.VERSION,
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Set up static files and templates
setup_static_files(app)
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

# Include API router
app.include_router(api_router, prefix=settings.API_PREFIX)

# Initialize database
@app.on_event("startup")
async def startup_db_client():
    """Initialize database connection on application startup."""
    try:
        await DatabaseManager.initialize()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

# Clean up on shutdown
@app.on_event("shutdown")
async def shutdown_db_client():
    """Close database connection on application shutdown."""
    await DatabaseManager.close()
    logger.info("Database connection closed")

# Serve React app for all other routes
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_app(request: Request, full_path: str):
    ""
    Serve the React application for all routes not handled by the API.
    This allows for client-side routing.
    """
    # Don't serve the app for API routes or static files
    if full_path.startswith(settings.API_PREFIX.lstrip("/")) or full_path.startswith("static/"):
        return {"detail": "Not Found"}
    
    return serve_react_app(request)

# Root endpoint
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root(request: Request):
    ""Serve the main React application."""
    return serve_react_app(request)

# Health check endpoint
@app.get("/health", include_in_schema=False)
async def health_check():
    ""Health check endpoint for load balancers and monitoring."""
    return {"status": "ok", "version": settings.VERSION}

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    ""Handle request validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )

@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: Exception):
    ""Handle 404 errors."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Not Found"},
    )

@app.exception_handler(500)
async def server_error_exception_handler(request: Request, exc: Exception):
    ""Handle 500 errors."""
    logger.error(f"Server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )

def create_app() -> FastAPI:
    ""Create and configure the FastAPI application."""
    return app

# For development with uvicorn
if __name__ == "__main__":
    import uvicorn
    
    # Ensure static files are copied from frontend build
    try:
        copy_static_files()
    except Exception as e:
        logger.warning(f"Failed to copy static files: {e}")
    
    # Run the application
    uvicorn.run(
        "edix.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        workers=settings.WORKERS,
        log_level=settings.LOG_LEVEL.lower(),
    )
