"""
Data models for Edix
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator
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
    """Data structure schema definition"""
    name: str
    description: str = ""
    fields: Dict[str, FieldSchema] = Field(default_factory=dict)
    indexes: List[List[str]] = Field(default_factory=list)
    unique_constraints: List[List[str]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Structure(BaseModel):
    """Data structure definition"""
    name: str
    schema_name: str
    data: List[Dict[str, Any]] = Field(default_factory=list)

class DataItem(BaseModel):
    """Single data item within a structure"""
    id: int
    data: Dict[str, Any]
    created_at: str
    updated_at: str

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
