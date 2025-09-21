"""
DataItem-related Pydantic models for request/response validation.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator, HttpUrl, ConfigDict

from .base import (
    BaseSchema, BaseCreateSchema, BaseUpdateSchema, 
    BaseInDBSchema, BaseResponseSchema
)

class DataItemStatus(str, Enum):
    """Status of a data item."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class DataItemBase(BaseSchema):
    """Base schema for data items."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    status: DataItemStatus = Field(default=DataItemStatus.DRAFT)
    data: Dict[str, Any] = Field(..., description="The actual data content")
    metadata_: Dict[str, Any] = Field(default_factory=dict, alias="metadata")
    tags: List[str] = Field(default_factory=list)
    
    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name must not be empty')
        return v.strip()
    
    @field_validator('data', 'metadata_')
    @classmethod
    def validate_json_fields(cls, v):
        if not isinstance(v, dict):
            raise ValueError('Must be a JSON object')
        return v
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if not isinstance(v, list):
            raise ValueError('Tags must be a list of strings')
        return [str(tag).strip() for tag in v if str(tag).strip()]

class DataItemCreate(DataItemBase, BaseCreateSchema):
    """Schema for creating a new data item."""
    structure_id: int = Field(..., description="ID of the parent structure")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "User Profile - John Doe",
                "description": "Profile information for John Doe",
                "status": "draft",
                "structure_id": 1,
                "data": {
                    "firstName": "John",
                    "lastName": "Doe",
                    "email": "john.doe@example.com",
                    "age": 30
                },
                "metadata": {
                    "source": "web_form",
                    "ip_address": "192.168.1.1"
                },
                "tags": ["user", "profile"]
            }
        }
    )

class DataItemUpdate(BaseUpdateSchema):
    """Schema for updating an existing data item."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[DataItemStatus] = None
    data: Optional[Dict[str, Any]] = None
    metadata_: Optional[Dict[str, Any]] = Field(None, alias="metadata")
    tags: Optional[List[str]] = None
    
    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Name must not be empty')
        return v.strip() if v else v
    
    @field_validator('data', 'metadata_')
    @classmethod
    def validate_json_fields(cls, v):
        if v is not None and not isinstance(v, dict):
            raise ValueError('Must be a JSON object')
        return v
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if v is not None and not isinstance(v, list):
            raise ValueError('Tags must be a list of strings')
        return [str(tag).strip() for tag in v] if v else None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated User Profile - John Doe",
                "description": "Updated profile information",
                "status": "published",
                "data": {
                    "firstName": "John",
                    "lastName": "Doe",
                    "email": "john.doe.updated@example.com",
                    "age": 31,
                    "phone": "+1234567890"
                },
                "metadata": {
                    "source": "web_form",
                    "ip_address": "192.168.1.1",
                    "updated_by": "admin@example.com"
                },
                "tags": ["user", "profile", "updated"]
            }
        }
    )

class DataItemInDB(DataItemBase, BaseInDBSchema):
    """Schema as stored in the database."""
    structure_id: int
    version: int = 1
    owner_id: int
    
    model_config = ConfigDict(
        fields={
            'metadata_': {'exclude': False},
            'data': {'exclude': False}
        }
    )

class DataItemResponse(DataItemInDB, BaseResponseSchema):
    """Schema for API responses."""
    pass

class BulkDataItemCreate(BaseModel):
    """Schema for creating multiple data items in bulk."""
    items: List[DataItemCreate]
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "name": "User 1",
                        "description": "First user",
                        "structure_id": 1,
                        "data": {"name": "Alice", "age": 25}
                    },
                    {
                        "name": "User 2",
                        "description": "Second user",
                        "structure_id": 1,
                        "data": {"name": "Bob", "age": 30}
                    }
                ]
            }
        }
    )

class DataItemSearch(BaseModel):
    """Schema for searching data items."""
    query: Optional[str] = None
    status: Optional[DataItemStatus] = None
    tags: Optional[List[str]] = None
    structure_id: Optional[int] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    updated_after: Optional[datetime] = None
    updated_before: Optional[datetime] = None
    limit: int = 100
    offset: int = 0
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "john",
                "status": "published",
                "tags": ["user", "profile"],
                "created_after": "2023-01-01T00:00:00",
                "limit": 10,
                "offset": 0
            }
        }
    )
