"""
Schema-related Pydantic models for request/response validation.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator, ConfigDict

from .base import (
    BaseSchema, BaseCreateSchema, BaseUpdateSchema, 
    BaseInDBSchema, BaseResponseSchema
)

class SchemaBase(BaseSchema):
    """Base schema for data schemas."""
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_public: bool = Field(default=True)
    
    @field_validator('name')
    @classmethod
    def name_must_be_valid(cls, v):
        if not v.replace('_', '').isalnum():
            raise ValueError('Name must be alphanumeric with underscores')
        return v.lower()

class SchemaCreate(SchemaBase, BaseCreateSchema):
    """Schema for creating a new data schema."""
    schema_definition: Dict[str, Any]
    
    @field_validator('schema_definition')
    @classmethod
    def validate_schema_definition(cls, v):
        if not isinstance(v, dict):
            raise ValueError('Schema definition must be a JSON object')
        
        # Basic validation of JSON Schema structure
        if 'type' not in v:
            raise ValueError("Schema must have a 'type' field")
            
        if v.get('type') == 'object' and 'properties' not in v:
            raise ValueError("Object schema must have a 'properties' field")
            
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "person",
                "description": "A person schema",
                "is_public": True,
                "schema_definition": {
                    "type": "object",
                    "required": ["name", "age"],
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "integer", "minimum": 0}
                    }
                }
            }
        }
    )

class SchemaUpdate(BaseUpdateSchema):
    """Schema for updating an existing data schema."""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_public: Optional[bool] = None
    schema_definition: Optional[Dict[str, Any]] = None
    
    @field_validator('name')
    @classmethod
    def name_must_be_valid(cls, v):
        if v is not None and not v.replace('_', '').isalnum():
            raise ValueError('Name must be alphanumeric with underscores')
        return v.lower() if v else v
    
    @field_validator('schema_definition')
    @classmethod
    def validate_schema_definition(cls, v):
        if v is not None and not isinstance(v, dict):
            raise ValueError('Schema definition must be a JSON object')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "updated_person",
                "description": "Updated person schema",
                "is_public": False,
                "schema_definition": {
                    "type": "object",
                    "required": ["name", "age", "email"],
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "integer", "minimum": 0},
                        "email": {"type": "string", "format": "email"}
                    }
                }
            }
        }
    )

class SchemaInDB(SchemaBase, BaseInDBSchema):
    """Schema as stored in the database."""
    schema_definition: Dict[str, Any]
    owner_id: int
    
    model_config = ConfigDict()

class SchemaResponse(SchemaInDB, BaseResponseSchema):
    """Schema for API responses."""
    pass

# Helper schemas for schema validation
class SchemaValidationError(BaseModel):
    """Represents a schema validation error."""
    path: str
    message: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "path": "age",
                "message": "-1 is less than the minimum of 0"
            }
        }
    )

class SchemaValidationResult(BaseModel):
    """Result of schema validation."""
    valid: bool
    errors: List[SchemaValidationError] = []
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "valid": False,
                "errors": [
                    {
                        "path": "age",
                        "message": "-1 is less than the minimum of 0"
                    }
                ]
            }
        }
    )
