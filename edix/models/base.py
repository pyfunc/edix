"""
Base SQLAlchemy models for the Edix application.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, String, Text, JSON, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func

from ..config import settings

# Type variables for generic model handling
ModelType = TypeVar("ModelType", bound="BaseModel")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

# SQLAlchemy base class
@as_declarative()
class Base:
    ""Base class for all SQLAlchemy models."""
    
    id: Any
    __name__: str
    
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(self) -> str:
        return self.__name__.lower()
    
    # Common columns
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class BaseCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    ""Base class for CRUD operations on models."""
    
    def __init__(self, model: Type[ModelType]):
        ""Initialize with the model class."""
        self.model = model
    
    async def get(self, db: Session, id: Any) -> Optional[ModelType]:
        ""Get a single record by ID."""
        return db.query(self.model).filter(self.model.id == id).first()
    
    async def get_multi(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        **filters: Any
    ) -> List[ModelType]:
        ""Get multiple records with optional filtering."""
        query = db.query(self.model)
        
        # Apply filters
        for field, value in filters.items():
            if hasattr(self.model, field):
                query = query.filter(getattr(self.model, field) == value)
        
        return query.offset(skip).limit(limit).all()
    
    async def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        ""Create a new record."""
        obj_in_data = obj_in.dict() if hasattr(obj_in, 'dict') else obj_in
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    async def update(
        self, 
        db: Session, 
        *, 
        db_obj: ModelType, 
        obj_in: UpdateSchemaType
    ) -> ModelType:
        ""Update an existing record."""
        obj_data = obj_in.dict(exclude_unset=True) if hasattr(obj_in, 'dict') else obj_in
        
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    async def remove(self, db: Session, *, id: Any) -> ModelType:
        ""Delete a record by ID."""
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
    
    async def soft_delete(self, db: Session, *, id: Any) -> Optional[ModelType]:
        ""Soft delete a record by setting deleted_at timestamp."""
        obj = await self.get(db, id)
        if obj and hasattr(obj, 'deleted_at'):
            obj.deleted_at = datetime.utcnow()
            db.add(obj)
            db.commit()
            db.refresh(obj)
        return obj
