"""
Structure-related Pydantic models for request/response validation.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator, HttpUrl

from .base import (
    BaseSchema, BaseCreateSchema, BaseUpdateSchema, 
    BaseInDBSchema, BaseResponseSchema
)

class StructureType(str, Enum):
    """Types of structures in the system."""
    COLLECTION = "collection"
    DOCUMENT = "document"
    TABLE = "table"
    GRAPH = "graph"
    CUSTOM = "custom"

class StructureStatus(str, Enum):
    """Status of a structure."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class StructureBase(BaseSchema):
    """Base schema for structures."""
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    structure_type: StructureType = Field(..., description="Type of the structure")
    status: StructureStatus = Field(default=StructureStatus.DRAFT)
    is_public: bool = Field(default=False)
    metadata_: Dict[str, Any] = Field(default_factory=dict, alias="metadata")
    schema_id: Optional[int] = Field(
        None, 
        description="ID of the schema this structure follows"
    )
    
    @validator('name')
    def name_must_be_valid(cls, v):
        if not v.replace('_', '').replace('-', '').replace(' ', '').isalnum():
            raise ValueError('Name must be alphanumeric with underscores, hyphens, or spaces')
        return v
    
    @validator('metadata_')
    def validate_metadata(cls, v):
        if not isinstance(v, dict):
            raise ValueError('Metadata must be a JSON object')
        return v

class StructureCreate(StructureBase, BaseCreateSchema):
    """Schema for creating a new structure."""
    class Config(StructureBase.Config):
        schema_extra = {
            "example": {
                "name": "user_profiles",
                "description": "User profile information",
                "structure_type": "document",
                "status": "draft",
                "is_public": False,
                "metadata": {
                    "category": "user_data",
                    "version": "1.0.0"
                },
                "schema_id": 1
            }
        }

class StructureUpdate(BaseUpdateSchema):
    """Schema for updating an existing structure."""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    structure_type: Optional[StructureType] = None
    status: Optional[StructureStatus] = None
    is_public: Optional[bool] = None
    metadata_: Optional[Dict[str, Any]] = Field(None, alias="metadata")
    schema_id: Optional[int] = None
    
    @validator('name')
    def name_must_be_valid(cls, v):
        if v is not None and not v.replace('_', '').replace('-', '').replace(' ', '').isalnum():
            raise ValueError('Name must be alphanumeric with underscores, hyphens, or spaces')
        return v
    
    @validator('metadata_')
    def validate_metadata(cls, v):
        if v is not None and not isinstance(v, dict):
            raise ValueError('Metadata must be a JSON object')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "name": "updated_user_profiles",
                "description": "Updated user profile information",
                "status": "published",
                "is_public": True,
                "metadata": {
                    "category": "user_data",
                    "version": "1.0.1"
                }
            }
        }

class StructureInDB(StructureBase, BaseInDBSchema):
    """Schema as stored in the database."""
    owner_id: int
    
    class Config(StructureBase.Config):
        fields = {
            'metadata_': {'exclude': False}
        }

class StructureResponse(StructureInDB, BaseResponseSchema):
    """Schema for API responses."""
    pass

class StructureStats(BaseModel):
    """Statistics about a structure."""
    item_count: int = 0
    status_distribution: Dict[str, int] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    
    class Config:
        schema_extra = {
            "example": {
                "item_count": 42,
                "status_distribution": {
                    "draft": 10,
                    "published": 30,
                    "archived": 2
                },
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-06-15T12:34:56",
                "last_updated": "2023-06-15T12:34:56"
            }
        }
