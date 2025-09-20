"""
CRUD operations for Structure model.
"""
from typing import Any, Dict, List, Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.structure import Structure, StructureCreate, StructureUpdate, StructureInDB
from .base import CRUDBaseWithOwner

class CRUDStructure(CRUDBaseWithOwner[Structure, StructureCreate, StructureUpdate]):
    """
    CRUD operations for Structure model with owner-specific methods.
    """
    
    async def get_by_name(
        self, 
        db: AsyncSession, 
        *, 
        name: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Structure]:
        """Get structures by name (case-insensitive search)."""
        result = await db.execute(
            select(self.model)
            .where(self.model.name.ilike(f"%{name}%"))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_name_and_owner(
        self, 
        db: AsyncSession, 
        *, 
        name: str, 
        owner_id: int
    ) -> Optional[Structure]:
        """Get a structure by name and owner ID."""
        result = await db.execute(
            select(self.model)
            .where(
                (self.model.name == name) & 
                (self.model.owner_id == owner_id)
            )
        )
        return result.scalars().first()
    
    async def get_public_structures(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Structure]:
        """Get all public structures."""
        result = await db.execute(
            select(self.model)
            .where(self.model.is_public == True)
            .where(self.model.status == "published")
            .offset(skip)
            .limit(limit)
            .order_by(self.model.name)
        )
        return result.scalars().all()
    
    async def get_by_schema(
        self,
        db: AsyncSession,
        *,
        schema_id: int,
        skip: int = 0,
        limit: int = 100,
        include_public: bool = False,
        current_user_id: Optional[int] = None,
    ) -> List[Structure]:
        """Get structures that use a specific schema."""
        query = select(self.model).where(self.model.schema_id == schema_id)
        
        if not include_public and current_user_id:
            query = query.where(self.model.owner_id == current_user_id)
        elif include_public and current_user_id:
            query = query.where(
                (self.model.owner_id == current_user_id) | 
                (self.model.is_public == True)
            )
        
        result = await db.execute(
            query.offset(skip).limit(limit).order_by(self.model.name)
        )
        return result.scalars().all()
    
    async def create_with_owner(
        self, 
        db: AsyncSession, 
        *, 
        obj_in: StructureCreate, 
        owner_id: int
    ) -> Structure:
        """Create a new structure with an owner."""
        # Check if structure with this name already exists for the owner
        existing_structure = await self.get_by_name_and_owner(
            db, name=obj_in.name, owner_id=owner_id
        )
        if existing_structure:
            raise ValueError(f"Structure with name '{obj_in.name}' already exists for this user")
        
        # Create the structure
        db_obj = self.model(
            name=obj_in.name,
            description=obj_in.description,
            structure_type=obj_in.structure_type,
            status=obj_in.status,
            is_public=obj_in.is_public,
            metadata_=obj_in.metadata_,
            owner_id=owner_id,
            schema_id=obj_in.schema_id,
        )
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: Structure, 
        obj_in: Union[StructureUpdate, Dict[str, Any]]
    ) -> Structure:
        """Update a structure."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        # If name is being updated, check for conflicts
        if "name" in update_data and update_data["name"] != db_obj.name:
            existing_structure = await self.get_by_name_and_owner(
                db, name=update_data["name"], owner_id=db_obj.owner_id
            )
            if existing_structure:
                raise ValueError(f"Structure with name '{update_data['name']}' already exists for this user")
        
        # Handle metadata update - merge with existing metadata
        if "metadata_" in update_data and update_data["metadata_"] is not None:
            if db_obj.metadata_:
                # Merge with existing metadata
                update_data["metadata_"] = {**db_obj.metadata_, **update_data["metadata_"]}
        
        return await super().update(db, db_obj=db_obj, obj_in=update_data)
    
    async def get_stats(
        self,
        db: AsyncSession,
        *,
        structure_id: int,
        current_user_id: int
    ) -> Dict[str, Any]:
        """
        Get statistics for a structure.
        
        Returns:
            Dict with structure statistics
        """
        from ..crud.crud_data_item import data_item_crud
        
        # Get the structure with related items
        structure = await self.get(db, id=structure_id)
        if not structure:
            raise ValueError("Structure not found")
        
        # Check if user has access to this structure
        if not structure.is_public and structure.owner_id != current_user_id:
            raise PermissionError("Not authorized to access this structure")
        
        # Get item count and status distribution
        items = await data_item_crud.get_multi_by_structure(
            db, structure_id=structure_id, limit=1000
        )
        
        status_dist = {}
        for item in items:
            status_dist[item.status] = status_dist.get(item.status, 0) + 1
        
        # Get last updated timestamp
        last_updated = None
        if items:
            last_updated = max(
                item.updated_at or item.created_at 
                for item in items 
                if item.updated_at or item.created_at
            )
        
        return {
            "structure_id": structure_id,
            "name": structure.name,
            "item_count": len(items),
            "status_distribution": status_dist,
            "created_at": structure.created_at.isoformat() if structure.created_at else None,
            "updated_at": structure.updated_at.isoformat() if structure.updated_at else None,
            "last_updated": last_updated.isoformat() if last_updated else None,
        }

# Create a singleton instance
structure_crud = CRUDStructure(Structure)
