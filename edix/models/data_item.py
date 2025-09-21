"""
Data Item model and related functionality for storing structured data.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, ConfigDict
from sqlalchemy import Column, DateTime, String, Text, JSON, Boolean, ForeignKey, Index, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base, BaseCRUD

# Enums
class DataItemStatus(str, Enum):
    """Status of a data item."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

# Pydantic models
class DataItemBase(BaseModel):
    """Base data item model with common attributes."""
    name: str = Field(..., description="Name or title of the data item")
    description: Optional[str] = Field(None, description="Description of the data item")
    status: DataItemStatus = Field(
        DataItemStatus.DRAFT, 
        description="Status of the data item"
    )
    metadata_: Optional[Dict[str, Any]] = Field(
        None, 
        alias="metadata", 
        description="Additional metadata for the data item"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "name": "User Profile - John Doe",
                "description": "Profile data for John Doe",
                "status": "draft",
                "metadata": {
                    "tags": ["user", "profile"],
                    "version": "1.0.0"
                }
            }
        }
    )

class DataItemCreate(DataItemBase):
    """Model for creating a new data item."""
    data: Dict[str, Any] = Field(..., description="The actual data content")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Data item name cannot be empty')
        return v.strip()
    
    @field_validator('data')
    @classmethod
    def validate_data(cls, v):
        if not isinstance(v, dict):
            raise ValueError('Data must be a dictionary')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "User Profile - John Doe",
                "description": "Profile data for John Doe",
                "status": "draft",
                "metadata": {
                    "tags": ["user", "profile"],
                    "version": "1.0.0"
                },
                "data": {
                    "username": "johndoe",
                    "email": "john.doe@example.com",
                    "firstName": "John",
                    "lastName": "Doe",
                    "age": 30
                }
            }
        }
    )

class DataItemUpdate(BaseModel):
    """Model for updating an existing data item."""
    name: Optional[str] = Field(None, description="Name or title of the data item")
    description: Optional[str] = Field(None, description="Description of the data item")
    status: Optional[DataItemStatus] = Field(None, description="Status of the data item")
    data: Optional[Dict[str, Any]] = Field(None, description="The actual data content")
    metadata: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional metadata for the data item"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Updated User Profile - John Doe",
                "description": "Updated profile data for John Doe",
                "status": "published",
                "data": {
                    "username": "johndoe",
                    "email": "john.doe.updated@example.com",
                    "firstName": "John",
                    "lastName": "Doe",
                    "age": 31
                },
                "metadata": {
                    "tags": ["user", "profile", "updated"],
                    "version": "1.1.0"
                }
            }
        }
    )

class DataItemInDBBase(DataItemBase):
    """Base model for data item stored in database."""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner_id: UUID
    structure_id: UUID
    
    model_config = ConfigDict(from_attributes=True)

class DataItem(DataItemInDBBase):
    """Data item model for API responses."""
    data: Dict[str, Any] = Field(..., description="The actual data content")
    version: int = Field(1, description="Version number of the data item")

class DataItemInDB(DataItemInDBBase):
    """Data item model with raw data for database storage."""
    data: Dict[str, Any] = Field(..., description="The actual data content")
    version: int = Field(1, description="Version number of the data item")

# SQLAlchemy model
class DBDataItem(Base):
    """SQLAlchemy data item model."""
    __tablename__ = "data_items"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="draft")
    data = Column(JSONB, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    metadata_ = Column("metadata", JSONB, nullable=True)
    owner_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    structure_id = Column(PG_UUID(as_uuid=True), ForeignKey("structures.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("DBUser", back_populates="data_items")
    structure = relationship("DBStructure", back_populates="items")
    
    # Indexes
    __table_args__ = (
        Index("idx_data_item_structure", "structure_id"),
        Index("idx_data_item_owner", "owner_id"),
        Index("idx_data_item_status", "status"),
        Index("idx_data_item_created", "created_at"),
    )
    
    def __repr__(self):
        return f"<DataItem {self.name} ({self.status})>"
    
    def to_dict(self):
        """Convert the data item to a dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "data": self.data,
            "version": self.version,
            "metadata": self.metadata_,
            "owner_id": str(self.owner_id),
            "structure_id": str(self.structure_id),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

# CRUD operations
class DataItemCRUD(BaseCRUD[DBDataItem, DataItemCreate, DataItemUpdate]):
    """CRUD operations for data items."""
    
    async def get_multi_by_structure(
        self, 
        db, 
        *, 
        structure_id: UUID, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[DBDataItem]:
        """Get multiple data items by structure ID, optionally filtered by status."""
        query = db.query(self.model).filter(self.model.structure_id == structure_id)
        
        if status:
            query = query.filter(self.model.status == status)
            
        return query.order_by(self.model.created_at.desc()).offset(skip).limit(limit).all()
    
    async def get_multi_by_owner(
        self, 
        db, 
        *, 
        owner_id: UUID, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[DBDataItem]:
        """Get multiple data items by owner ID."""
        return (
            db.query(self.model)
            .filter(self.model.owner_id == owner_id)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    async def create_with_owner(
        self, 
        db, 
        *, 
        obj_in: DataItemCreate, 
        owner_id: UUID,
        structure_id: UUID
    ) -> DBDataItem:
        """Create a new data item with an owner and structure."""
        db_obj = self.model(
            name=obj_in.name,
            description=obj_in.description,
            status=obj_in.status,
            data=obj_in.data,
            metadata_=obj_in.metadata_,
            owner_id=owner_id,
            structure_id=structure_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    async def update(
        self, 
        db, 
        *, 
        db_obj: DBDataItem, 
        obj_in: DataItemUpdate
    ) -> DBDataItem:
        """Update a data item, handling versioning."""
        update_data = obj_in.dict(exclude_unset=True)
        
        # Handle metadata update to merge with existing metadata
        if "metadata" in update_data and update_data["metadata"] is not None:
            current_metadata = db_obj.metadata_ or {}
            current_metadata.update(update_data["metadata"])
            update_data["metadata_"] = current_metadata
            del update_data["metadata"]
        
        # Increment version if data is being updated
        if "data" in update_data and update_data["data"] is not None:
            update_data["version"] = (db_obj.version or 0) + 1
        
        return await super().update(db, db_obj=db_obj, obj_in=update_data)
    
    async def search(
        self,
        db,
        *,
        query: str,
        structure_id: Optional[UUID] = None,
        owner_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[DBDataItem]:
        """Search data items by text query in name, description, or data."""
        search = f"%{query}%"
        
        q = db.query(self.model).filter(
            (self.model.name.ilike(search)) |
            (self.model.description.ilike(search)) |
            (self.model.data.cast(String).ilike(search))
        )
        
        if structure_id:
            q = q.filter(self.model.structure_id == structure_id)
            
        if owner_id:
            q = q.filter(self.model.owner_id == owner_id)
        
        return q.order_by(self.model.created_at.desc()).offset(skip).limit(limit).all()
