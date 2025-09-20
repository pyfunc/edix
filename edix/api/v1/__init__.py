"""
API v1 Router

This module contains all the API v1 endpoints.
"""
from fastapi import APIRouter

from .endpoints import auth, users, schemas, structures, data_items

# Create the API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(schemas.router, prefix="/schemas", tags=["Schemas"])
api_router.include_router(structures.router, prefix="/structures", tags=["Structures"])
api_router.include_router(data_items.router, prefix="/data", tags=["Data Items"])
