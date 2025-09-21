"""
CRUD operations for Schema model.
"""
from typing import Any, Dict, List, Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.schema import DBSchema
from ..schemas.schema import SchemaCreate, SchemaUpdate, SchemaInDB
from .base import CRUDBase, CRUDBaseWithOwner

class CRUDSchema(CRUDBaseWithOwner[DBSchema, SchemaCreate, SchemaUpdate]):
    """
    CRUD operations for Schema model with owner-specific methods.
    """
    
    async def get_by_name(
        self, 
        db: AsyncSession, 
        *, 
        name: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[DBSchema]:
        """Get schemas by name (case-insensitive search)."""
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
    ) -> Optional[DBSchema]:
        """Get a schema by name and owner ID."""
        result = await db.execute(
            select(self.model)
            .where(
                (self.model.name == name) & 
                (self.model.owner_id == owner_id)
            )
        )
        return result.scalars().first()
    
    async def get_public_schemas(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[DBSchema]:
        """Get all public schemas."""
        result = await db.execute(
            select(self.model)
            .where(self.model.is_public == True)
            .offset(skip)
            .limit(limit)
            .order_by(self.model.name)
        )
        return result.scalars().all()
    
    async def create_with_owner(
        self, 
        db: AsyncSession, 
        *, 
        obj_in: SchemaCreate, 
        owner_id: int
    ) -> DBSchema:
        """Create a new schema with an owner."""
        # Check if schema with this name already exists for the owner
        existing_schema = await self.get_by_name_and_owner(
            db, name=obj_in.name, owner_id=owner_id
        )
        if existing_schema:
            raise ValueError(f"Schema with name '{obj_in.name}' already exists for this user")
        
        # Create the schema
        db_obj = self.model(
            name=obj_in.name,
            description=obj_in.description,
            schema_definition=obj_in.schema_definition,
            is_public=obj_in.is_public,
            owner_id=owner_id,
        )
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: DBSchema, 
        obj_in: Union[SchemaUpdate, Dict[str, Any]]
    ) -> DBSchema:
        """Update a schema."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        # If name is being updated, check for conflicts
        if "name" in update_data and update_data["name"] != db_obj.name:
            existing_schema = await self.get_by_name_and_owner(
                db, name=update_data["name"], owner_id=db_obj.owner_id
            )
            if existing_schema:
                raise ValueError(f"Schema with name '{update_data['name']}' already exists for this user")
        
        return await super().update(db, db_obj=db_obj, obj_in=update_data)
    
    async def validate_data(
        self,
        db: AsyncSession,
        *,
        schema_id: int,
        data: Dict[str, Any],
        current_user_id: int
    ) -> Dict[str, Any]:
        """
        Validate data against a schema.
        
        Returns:
            Dict with validation results including:
            - valid: bool - Whether the data is valid
            - errors: List[str] - List of validation errors, if any
        """
        schema = await self.get(db, id=schema_id)
        if not schema:
            raise ValueError("Schema not found")
        
        # Check if user has access to this schema
        if not schema.is_public and schema.owner_id != current_user_id:
            raise PermissionError("Not authorized to access this schema")
        
        # TODO: Implement actual schema validation logic
        # This is a placeholder implementation
        errors = []
        
        # Example validation: Check required fields
        required_fields = schema.schema_definition.get("required", [])
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Example validation: Check field types
        properties = schema.schema_definition.get("properties", {})
        for field, value in data.items():
            if field not in properties:
                # Skip fields not in schema (or make this an error if desired)
                continue
                
            field_def = properties[field]
            field_type = field_def.get("type")
            
            if field_type == "string" and not isinstance(value, str):
                errors.append(f"Field '{field}' must be a string")
            elif field_type == "number" and not isinstance(value, (int, float)):
                errors.append(f"Field '{field}' must be a number")
            elif field_type == "integer" and not isinstance(value, int):
                errors.append(f"Field '{field}' must be an integer")
            elif field_type == "boolean" and not isinstance(value, bool):
                errors.append(f"Field '{field}' must be a boolean")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "schema_id": schema_id,
            "schema_name": schema.name,
        }

# Create a singleton instance
schema_crud = CRUDSchema(DBSchema)
