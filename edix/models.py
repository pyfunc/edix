"""
Pydantic models for validation
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class FieldType(str, Enum):
    """Supported field types"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    DATE = "date"
    TIME = "time"
    JSON = "json"
    RELATION = "relation"


class FieldSchema(BaseModel):
    """Schema definition for a single field"""
    type: FieldType
    required: bool = True
    default: Any = None
    description: str = ""
    max_length: Optional[int] = None
    min_length: Optional[int] = None
    regex: Optional[str] = None
    enum: Optional[List[Any]] = None
    format: Optional[str] = None
    relation: Optional[Dict[str, str]] = None


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


class APIResponse(BaseModel):
    """Standard API response"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    @classmethod
    def success_response(cls, message: str, data: Optional[Dict[str, Any]] = None):
        """Create a success response"""
        return cls(success=True, message=message, data=data)

    @classmethod
    def error_response(cls, message: str, error: Optional[str] = None):
        """Create an error response"""
        return cls(success=False, message=message, error=error or message)
