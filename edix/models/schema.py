"""
Schema model and related functionality.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, DateTime, String, Text, JSON, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base, BaseCRUD

# Enums
class SchemaType(str, Enum):
    ""Types of schemas supported by the system."""
    JSON_SCHEMA = "json_schema"
    OPEN_API = "open_api"
    GRAPHQL = "graphql"
    PROTOBUF = "protobuf"
    AVRO = "avro"
    CUSTOM = "custom"

# Pydantic models
class SchemaField(BaseModel):
    ""A single field in a schema."""
    name: str = Field(..., description="Name of the field")
    type: str = Field(..., description="Data type of the field")
    required: bool = Field(True, description="Whether the field is required")
    description: Optional[str] = Field(None, description="Description of the field")
    default: Optional[Any] = Field(None, description="Default value for the field")
    constraints: Optional[Dict[str, Any]] = Field(
        None, 
        description="Validation constraints for the field"
    )

class SchemaBase(BaseModel):
    ""Base schema model with common attributes."""
    name: str = Field(..., description="Name of the schema")
    description: Optional[str] = Field(None, description="Description of the schema")
    schema_type: SchemaType = Field(
        SchemaType.JSON_SCHEMA, 
        description="Type of the schema"
    )
    version: str = Field("1.0.0", description="Version of the schema")
    is_active: bool = Field(True, description="Whether the schema is active")
    metadata_: Optional[Dict[str, Any]] = Field(
        None, 
        alias="metadata", 
        description="Additional metadata for the schema"
    )
    
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "name": "UserProfile",
                "description": "Schema for user profile data",
                "schema_type": "json_schema",
                "version": "1.0.0",
                "is_active": True,
                "metadata": {
                    "author": "System",
                    "tags": ["user", "profile"]
                }
            }
        }

class SchemaCreate(SchemaBase):
    ""Model for creating a new schema."""
    fields: List[SchemaField] = Field(..., description="List of fields in the schema")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Schema name cannot be empty')
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "name": "UserProfile",
                "description": "Schema for user profile data",
                "schema_type": "json_schema",
                "version": "1.0.0",
                "is_active": True,
                "metadata": {
                    "author": "System",
                    "tags": ["user", "profile"]
                },
                "fields": [
                    {
                        "name": "username",
                        "type": "string",
                        "required": True,
                        "description": "User's username",
                        "constraints": {
                            "minLength": 3,
                            "maxLength": 50
                        }
                    },
                    {
                        "name": "email",
                        "type": "string",
                        "required": True,
                        "description": "User's email address",
                        "constraints": {
                            "format": "email"
                        }
                    }
                ]
            }
        }

class SchemaUpdate(BaseModel):
    ""Model for updating an existing schema."""
    name: Optional[str] = Field(None, description="Name of the schema")
    description: Optional[str] = Field(None, description="Description of the schema")
    version: Optional[str] = Field(None, description="Version of the schema")
    is_active: Optional[bool] = Field(None, description="Whether the schema is active")
    metadata: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional metadata for the schema"
    )
    fields: Optional[List[SchemaField]] = Field(
        None, 
        description="List of fields in the schema"
    )
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "name": "UpdatedUserProfile",
                "description": "Updated schema for user profile data",
                "version": "1.1.0",
                "is_active": True,
                "metadata": {
                    "author": "Admin",
                    "tags": ["user", "profile", "updated"]
                }
            }
        }

class SchemaInDBBase(SchemaBase):
    ""Base model for schema stored in database."""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class Schema(SchemaInDBBase):
    ""Schema model for API responses."""
    fields: List[Dict[str, Any]] = Field(..., description="List of fields in the schema")

class SchemaInDB(SchemaInDBBase):
    ""Schema model with raw data for database storage."""
    fields: List[Dict[str, Any]] = Field(..., description="Raw field definitions")
    owner_id: Optional[UUID] = Field(None, description="ID of the user who owns this schema")

# SQLAlchemy model
class DBSchema(Base):
    ""SQLAlchemy schema model."""
    __tablename__ = "schemas"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    schema_type = Column(String(50), nullable=False, default="json_schema")
    version = Column(String(50), nullable=False, default="1.0.0")
    is_active = Column(Boolean, default=True, nullable=False)
    fields = Column(JSONB, nullable=False)
    metadata_ = Column("metadata", JSONB, nullable=True)
    owner_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("DBUser", back_populates="schemas")
    structures = relationship("DBStructure", back_populates="schema")
    
    # Indexes
    __table_args__ = (
        Index("idx_schema_name_type", "name", "schema_type", unique=True),
    )
    
    def __repr__(self):
        return f"<Schema {self.name} ({self.schema_type})>"
    
    def to_dict(self):
        ""Convert the schema to a dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "schema_type": self.schema_type,
            "version": self.version,
            "is_active": self.is_active,
            "fields": self.fields,
            "metadata": self.metadata_,
            "owner_id": str(self.owner_id) if self.owner_id else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

# CRUD operations
class SchemaCRUD(BaseCRUD[DBSchema, SchemaCreate, SchemaUpdate]):
    ""CRUD operations for schemas."""
    
    async def get_by_name(
        self, db, *, name: str, schema_type: Optional[str] = None
    ) -> Optional[DBSchema]:
        ""Get a schema by name and optionally by type."""
        query = db.query(self.model).filter(self.model.name == name)
        if schema_type:
            query = query.filter(self.model.schema_type == schema_type)
        return query.first()
    
    async def get_multi_by_owner(
        self, db, *, owner_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[DBSchema]:
        ""Get multiple schemas by owner."""
        return (
            db.query(self.model)
            .filter(self.model.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    async def create_with_owner(
        self, db, *, obj_in: SchemaCreate, owner_id: UUID
    ) -> DBSchema:
        ""Create a new schema with an owner."""
        db_obj = self.model(
            name=obj_in.name,
            description=obj_in.description,
            schema_type=obj_in.schema_type,
            version=obj_in.version,
            is_active=obj_in.is_active,
            metadata_=obj_in.metadata_,
            fields=[field.dict() for field in obj_in.fields],
            owner_id=owner_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    async def update(
        self, db, *, db_obj: DBSchema, obj_in: SchemaUpdate
    ) -> DBSchema:
        ""Update a schema."""
        update_data = obj_in.dict(exclude_unset=True)
        
        # Handle fields update if provided
        if "fields" in update_data and update_data["fields"] is not None:
            # Convert SchemaField objects to dictionaries
            update_data["fields"] = [
                field.dict() if hasattr(field, "dict") else field
                for field in update_data["fields"]
            ]
        
        return await super().update(db, db_obj=db_obj, obj_in=update_data)
