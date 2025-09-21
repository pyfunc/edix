"""
Structure model and related functionality.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, ConfigDict
from sqlalchemy import Column, DateTime, String, Text, JSON, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base, BaseCRUD

# Enums
class StructureStatus(str, Enum):
    """Status of a structure."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class StructureType(str, Enum):
    """Types of structures supported by the system."""
    COLLECTION = "collection"
    DOCUMENT = "document"
    TABLE = "table"
    GRAPH = "graph"
    CUSTOM = "custom"

# Pydantic models
class StructureBase(BaseModel):
    """Base structure model with common attributes."""
    name: str = Field(..., description="Name of the structure")
    description: Optional[str] = Field(None, description="Description of the structure")
    structure_type: StructureType = Field(
        StructureType.COLLECTION, 
        description="Type of the structure"
    )
    status: StructureStatus = Field(
        StructureStatus.DRAFT, 
        description="Status of the structure"
    )
    is_public: bool = Field(
        False, 
        description="Whether the structure is publicly accessible"
    )
    metadata_: Optional[Dict[str, Any]] = Field(
        None, 
        alias="metadata", 
        description="Additional metadata for the structure"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "name": "UserProfiles",
                "description": "Collection of user profiles",
                "structure_type": "collection",
                "status": "draft",
                "is_public": False,
                "metadata": {
                    "tags": ["users", "profiles"],
                    "version": "1.0.0"
                }
            }
        }
    )

class StructureCreate(StructureBase):
    """Model for creating a new structure."""
    schema_id: Optional[UUID] = Field(
        None, 
        description="ID of the schema this structure is based on"
    )
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Structure name cannot be empty')
        return v.strip()
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "UserProfiles",
                "description": "Collection of user profiles",
                "structure_type": "collection",
                "status": "draft",
                "is_public": False,
                "metadata": {
                    "tags": ["users", "profiles"],
                    "version": "1.0.0"
                },
                "schema_id": "00000000-0000-0000-0000-000000000000"
            }
        }
    )

class StructureUpdate(BaseModel):
    """Model for updating an existing structure."""
    name: Optional[str] = Field(None, description="Name of the structure")
    description: Optional[str] = Field(None, description="Description of the structure")
    status: Optional[StructureStatus] = Field(None, description="Status of the structure")
    is_public: Optional[bool] = Field(None, description="Whether the structure is public")
    metadata: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional metadata for the structure"
    )
    schema_id: Optional[UUID] = Field(
        None, 
        description="ID of the schema this structure is based on"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "UpdatedUserProfiles",
                "description": "Updated collection of user profiles",
                "status": "published",
                "is_public": True,
                "metadata": {
                    "tags": ["users", "profiles", "v2"],
                    "version": "2.0.0"
                }
            }
        }
    )

class StructureInDBBase(StructureBase):
    """Base model for structure stored in database."""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner_id: UUID
    schema_id: Optional[UUID]
    
    model_config = ConfigDict(from_attributes=True)

class Structure(StructureInDBBase):
    """Structure model for API responses."""
    item_count: int = Field(0, description="Number of items in the structure")

class StructureInDB(StructureInDBBase):
    """"Structure model with raw data for database storage."""
    pass

# SQLAlchemy model
class DBStructure(Base):
    """SQLAlchemy structure model."""
    __tablename__ = "structures"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    structure_type = Column(String(50), nullable=False, default="collection")
    status = Column(String(50), nullable=False, default="draft")
    is_public = Column(Boolean, default=False, nullable=False)
    metadata_ = Column("metadata", JSONB, nullable=True)
    owner_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    schema_id = Column(PG_UUID(as_uuid=True), ForeignKey("schemas.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("DBUser", back_populates="structures")
    schema = relationship("DBSchema", back_populates="structures")
    items = relationship("DBDataItem", back_populates="structure", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_structure_owner", "owner_id"),
        Index("idx_structure_schema", "schema_id"),
        Index("idx_structure_status", "status"),
    )
    
    def __repr__(self):
        return f"<Structure {self.name} ({self.structure_type})>"
    
    def to_dict(self):
        """Convert the structure to a dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "structure_type": self.structure_type,
            "status": self.status,
            "is_public": self.is_public,
            "metadata": self.metadata_,
            "owner_id": str(self.owner_id),
            "schema_id": str(self.schema_id) if self.schema_id else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "item_count": len(self.items) if hasattr(self, 'items') else 0
        }

# CRUD operations
class StructureCRUD(BaseCRUD[DBStructure, StructureCreate, StructureUpdate]):
    """CRUD operations for structures."""
    
    async def get_multi_by_owner(
        self, 
        db, 
        *, 
        owner_id: UUID, 
        skip: int = 0, 
        limit: int = 100,
        include_public: bool = False
    ) -> List[DBStructure]:
        """Get multiple structures by owner, optionally including public ones."""
        query = db.query(self.model).filter(self.model.owner_id == owner_id)
        
        if include_public:
            query = query.filter(
                (self.model.owner_id == owner_id) | (self.model.is_public == True)
            )
        
        return query.offset(skip).limit(limit).all()
    
    async def get_public_structures(
        self, 
        db, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[DBStructure]:
        """Get all public structures."""
        return (
            db.query(self.model)
            .filter(self.model.is_public == True)
            .filter(self.model.status == "published")
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    async def create_with_owner(
        self, 
        db, 
        *, 
        obj_in: StructureCreate, 
        owner_id: UUID
    ) -> DBStructure:
        """Create a new structure with an owner."""
        db_obj = self.model(
            name=obj_in.name,
            description=obj_in.description,
            structure_type=obj_in.structure_type,
            status=obj_in.status,
            is_public=obj_in.is_public,
            metadata_=obj_in.metadata_,
            owner_id=owner_id,
            schema_id=obj_in.schema_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    async def update(
        self, 
        db, 
        *, 
        db_obj: DBStructure, 
        obj_in: StructureUpdate
    ) -> DBStructure:
        """Update a structure."""
        update_data = obj_in.dict(exclude_unset=True)
        
        # Handle metadata update to merge with existing metadata
        if "metadata" in update_data and update_data["metadata"] is not None:
            current_metadata = db_obj.metadata_ or {}
            current_metadata.update(update_data["metadata"])
            update_data["metadata_"] = current_metadata
            del update_data["metadata"]
        
        return await super().update(db, db_obj=db_obj, obj_in=update_data)
