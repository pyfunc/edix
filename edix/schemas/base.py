"""
Base Pydantic schemas for the application.

This module contains the base schemas that other schemas will inherit from.
"""
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict

# Type variables for generic models
T = TypeVar('T')

class BaseSchema(BaseModel):
    """Base schema with common fields and configuration."""
    model_config = ConfigDict(
        from_attributes=True,  # Replaces orm_mode in Pydantic v2
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        },
        extra='ignore',
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

class BaseCreateSchema(BaseSchema):
    """Schema for creating new records.

    This schema is used for creating new records and typically doesn't include
    fields that are set by the server (like IDs, timestamps, etc.).
    """
    pass

class BaseUpdateSchema(BaseSchema):
    """
    Schema for updating existing records.
    
    All fields are optional since partial updates are allowed.
    """
    pass

class BaseInDBSchema(BaseSchema):
    """
    Base schema for database models.
    
    Includes common fields that are present in most database models.
    """
    id: int
    created_at: datetime
    updated_at: datetime
    
    @field_validator('created_at', 'updated_at', mode='before')
    @classmethod
    def parse_dates(cls, value):
        """Parse string dates to datetime objects."""
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return value
        return value

class BaseResponseSchema(BaseInDBSchema):
    """
    Base schema for API responses.
    
    This schema is used for all API responses and includes metadata
    that might be useful for the client.
    """
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )

class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response schema.
    
    This schema is used for paginated list responses.
    """
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )

def create_response_schema(
    name: str,
    base_model: Type[BaseSchema],
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None
) -> Type[BaseModel]:
    """
    Create a response schema based on a base model.
    
    Args:
        name: The name of the new schema class
        base_model: The base model to create the schema from
        include: Fields to include (if None, all fields are included)
        exclude: Fields to exclude
        
    Returns:
        A new Pydantic model class
    """
    # Get the model fields
    model_fields = {
        k: v
        for k, v in base_model.model_fields.items()
        if (include is None or k in include)
        and (exclude is None or k not in exclude)
    }
    
    # Create the new model
    return type(
        name,
        (BaseResponseSchema,),
        {
            'model_fields': model_fields,
            'model_config': {
                'from_attributes': True,
                'json_encoders': {
                    **getattr(base_model.model_config, 'json_encoders', {})
                }
            }
        }
    )
