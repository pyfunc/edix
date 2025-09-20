"""
CRUD operations for DataItem model.
"""
from typing import Any, Dict, List, Optional, Union, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_

from ..models.data_item import DataItem, DataItemCreate, DataItemUpdate, DataItemInDB
from .base import CRUDBase, CRUDBaseWithOwner

class CRUDDataItem(CRUDBaseWithOwner[DataItem, DataItemCreate, DataItemUpdate]):
    """
    CRUD operations for DataItem model with owner-specific methods.
    """
    
    async def get_multi_by_structure(
        self, 
        db: AsyncSession, 
        *, 
        structure_id: int, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,
        order_by: str = "created_at",
        order: str = "desc"
    ) -> List[DataItem]:
        """Get multiple data items by structure ID with optional status filter."""
        query = select(self.model).where(self.model.structure_id == structure_id)
        
        if status:
            query = query.where(self.model.status == status)
        
        # Handle ordering
        order_column = getattr(self.model, order_by, None)
        if order_column is not None:
            if order.lower() == "desc":
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column)
        
        result = await db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()
    
    async def search(
        self,
        db: AsyncSession,
        *,
        query: str,
        structure_id: Optional[int] = None,
        owner_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[DataItem]:
        """Search data items by text query in name, description, or data."""
        search = f"%{query}%"
        
        # Build the base query
        stmt = select(self.model).where(
            or_(
                self.model.name.ilike(search),
                self.model.description.ilike(search),
                self.model.data.cast(String).ilike(search)
            )
        )
        
        # Add filters if provided
        if structure_id is not None:
            stmt = stmt.where(self.model.structure_id == structure_id)
            
        if owner_id is not None:
            stmt = stmt.where(self.model.owner_id == owner_id)
        
        # Execute the query
        result = await db.execute(stmt.offset(skip).limit(limit))
        return result.scalars().all()
    
    async def get_status_distribution(
        self, 
        db: AsyncSession, 
        *, 
        structure_id: int
    ) -> Dict[str, int]:
        """Get the distribution of statuses for data items in a structure."""
        result = await db.execute(
            select(
                self.model.status,
                func.count(self.model.id).label("count")
            )
            .where(self.model.structure_id == structure_id)
            .group_by(self.model.status)
        )
        
        return {row[0]: row[1] for row in result.all()}
    
    async def create_with_owner(
        self, 
        db: AsyncSession, 
        *, 
        obj_in: DataItemCreate, 
        owner_id: int,
        structure_id: int
    ) -> DataItem:
        """Create a new data item with an owner and structure."""
        # Check if structure exists and user has access
        from ..crud.crud_structure import structure_crud
        structure = await structure_crud.get(db, id=structure_id)
        if not structure:
            raise ValueError(f"Structure with ID {structure_id} not found")
        
        # If structure has a schema, validate the data against it
        if structure.schema_id:
            from ..crud.crud_schema import schema_crud
            validation = await schema_crud.validate_data(
                db, 
                schema_id=structure.schema_id,
                data=obj_in.data,
                current_user_id=owner_id
            )
            if not validation["valid"]:
                raise ValueError(
                    f"Data validation failed: {', '.join(validation['errors'])}"
                )
        
        # Create the data item
        db_obj = self.model(
            **obj_in.dict(exclude={"structure_id"}),
            owner_id=owner_id,
            structure_id=structure_id,
        )
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: DataItem, 
        obj_in: Union[DataItemUpdate, Dict[str, Any]]
    ) -> DataItem:
        """Update a data item, handling versioning."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        # If data is being updated, increment version
        if "data" in update_data and update_data["data"] != db_obj.data:
            update_data["version"] = (db_obj.version or 0) + 1
        
        return await super().update(db, db_obj=db_obj, obj_in=update_data)
    
    async def bulk_create(
        self,
        db: AsyncSession,
        *,
        items: List[DataItemCreate],
        owner_id: int,
        structure_id: int
    ) -> List[DataItem]:
        """Create multiple data items in a single transaction."""
        from ..crud.crud_structure import structure_crud
        
        # Check if structure exists and user has access
        structure = await structure_crud.get(db, id=structure_id)
        if not structure:
            raise ValueError(f"Structure with ID {structure_id} not found")
        
        # If structure has a schema, validate all items
        if structure.schema_id:
            from ..crud.crud_schema import schema_crud
            for item in items:
                validation = await schema_crud.validate_data(
                    db, 
                    schema_id=structure.schema_id,
                    data=item.data,
                    current_user_id=owner_id
                )
                if not validation["valid"]:
                    raise ValueError(
                        f"Data validation failed for item: {', '.join(validation['errors'])}"
                    )
        
        # Create all items
        db_objs = []
        for item in items:
            db_obj = self.model(
                **item.dict(exclude={"structure_id"}),
                owner_id=owner_id,
                structure_id=structure_id,
            )
            db.add(db_obj)
            db_objs.append(db_obj)
        
        await db.commit()
        
        # Refresh all objects to get their database-generated values
        for db_obj in db_objs:
            await db.refresh(db_obj)
        
        return db_objs
    
    async def get_field_stats(
        self,
        db: AsyncSession,
        *,
        structure_id: int,
        field: str,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get statistics for a specific field in a structure's data items."""
        # Build the query
        query = select(
            func.count().label("total"),
            func.count(getattr(self.model.data[field], "astext")),
            func.min(getattr(self.model.data[field], "astext").cast(String)),
            func.max(getattr(self.model.data[field], "astext").cast(String)),
            func.avg(getattr(self.model.data[field], "astext").cast(Float)),
            func.percentile_cont(0.5).within_group(
                getattr(self.model.data[field], "astext").cast(Float)
            ),
        ).where(self.model.structure_id == structure_id)
        
        if status:
            query = query.where(self.model.status == status)
        
        result = await db.execute(query)
        row = result.first()
        
        if not row:
            return {}
        
        total, non_null, min_val, max_val, avg_val, median_val = row
        
        return {
            "field": field,
            "total_count": total,
            "non_null_count": non_null,
            "null_count": total - non_null,
            "min": min_val,
            "max": max_val,
            "avg": float(avg_val) if avg_val is not None else None,
            "median": float(median_val) if median_val is not None else None,
        }

# Create a singleton instance
data_item_crud = CRUDDataItem(DataItem)
