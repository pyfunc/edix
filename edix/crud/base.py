"""
Base CRUD (Create, Read, Update, Delete) operations.
"""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_

from ..db.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base class for CRUD operations on SQLAlchemy models.
    
    Args:
        model: SQLAlchemy model class
    """
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """Get a single record by ID."""
        result = await db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalars().first()
    
    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records with pagination."""
        result = await db.execute(
            select(self.model).offset(skip).limit(limit).order_by(self.model.id)
        )
        return result.scalars().all()
    
    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record."""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: ModelType, 
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Update an existing record."""
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def remove(self, db: AsyncSession, *, id: int) -> ModelType:
        """Delete a record by ID."""
        obj = await self.get(db, id=id)
        if not obj:
            raise ValueError(f"{self.model.__name__} with ID {id} not found")
        
        await db.delete(obj)
        await db.commit()
        return obj
    
    async def get_by_field(
        self, 
        db: AsyncSession, 
        *, 
        field: str, 
        value: Any
    ) -> Optional[ModelType]:
        """Get a record by a specific field."""
        if not hasattr(self.model, field):
            raise AttributeError(f"{self.model.__name__} has no attribute {field}")
        
        result = await db.execute(
            select(self.model).where(getattr(self.model, field) == value)
        )
        return result.scalars().first()
    
    async def search(
        self,
        db: AsyncSession,
        *,
        query: str,
        field: str = "name",
        skip: int = 0,
        limit: int = 100,
    ) -> List[ModelType]:
        """Search records by text in a specific field."""
        if not hasattr(self.model, field):
            raise AttributeError(f"{self.model.__name__} has no attribute {field}")
        
        search = f"%{query}%"
        result = await db.execute(
            select(self.model)
            .where(getattr(self.model, field).ilike(search))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

class CRUDBaseWithOwner(CRUDBase[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base CRUD class for models with an owner.
    
    Extends CRUDBase with owner-specific operations.
    """
    
    async def create_with_owner(
        self, 
        db: AsyncSession, 
        *, 
        obj_in: CreateSchemaType, 
        owner_id: int
    ) -> ModelType:
        """Create a new record with an owner ID."""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, owner_id=owner_id)  # type: ignore
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_multi_by_owner(
        self, 
        db: AsyncSession, 
        *, 
        owner_id: int, 
        skip: int = 0, 
        limit: int = 100,
        include_public: bool = False
    ) -> List[ModelType]:
        """Get multiple records by owner ID."""
        query = select(self.model).where(self.model.owner_id == owner_id)
        
        if include_public and hasattr(self.model, 'is_public'):
            query = query.where(
                (self.model.owner_id == owner_id) | (self.model.is_public == True)
            )
        
        result = await db.execute(
            query.offset(skip).limit(limit).order_by(self.model.id)
        )
        return result.scalars().all()
    
    async def get_by_name_and_owner(
        self, 
        db: AsyncSession, 
        *, 
        name: str, 
        owner_id: int
    ) -> Optional[ModelType]:
        """Get a record by name and owner ID."""
        if not hasattr(self.model, 'name'):
            raise AttributeError(f"{self.model.__name__} has no attribute 'name'")
        
        result = await db.execute(
            select(self.model)
            .where(self.model.name == name, self.model.owner_id == owner_id)
        )
        return result.scalars().first()
