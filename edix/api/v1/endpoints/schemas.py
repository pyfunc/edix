"""
Schema management API endpoints.
"""
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from ....core.security import get_current_active_user
from ....crud.crud_schema import schema_crud
from ....db.deps import get_db
from ....models.schema import Schema, SchemaCreate, SchemaUpdate, SchemaInDB
from ....models.user import User
from ....schemas.msg import Msg

router = APIRouter()

@router.get("/", response_model=List[Schema])
async def read_schemas(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve schemas. Returns user's schemas plus public ones.
    """
    schemas = await schema_crud.get_multi_by_owner(
        db, owner_id=current_user.id, skip=skip, limit=limit, include_public=True
    )
    return schemas

@router.post("/", response_model=Schema)
async def create_schema(
    *,
    db: AsyncSession = Depends(get_db),
    schema_in: SchemaCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new schema.
    """
    # Check if schema with this name already exists for the user
    existing_schema = await schema_crud.get_by_name_and_owner(
        db, name=schema_in.name, owner_id=current_user.id
    )
    if existing_schema:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A schema with this name already exists for this user.",
        )
    
    schema = await schema_crud.create_with_owner(
        db, obj_in=schema_in, owner_id=current_user.id
    )
    return schema

@router.get("/public", response_model=List[Schema])
async def read_public_schemas(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve public schemas.
    """
    schemas = await schema_crud.get_public_schemas(db, skip=skip, limit=limit)
    return schemas

@router.get("/{schema_id}", response_model=Schema)
async def read_schema(
    schema_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get schema by ID.
    """
    schema = await schema_crud.get(db, id=schema_id)
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schema not found",
        )
    
    # Check if user has access to this schema
    if not schema.is_public and str(schema.owner_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return schema

@router.put("/{schema_id}", response_model=Schema)
async def update_schema(
    *,
    db: AsyncSession = Depends(get_db),
    schema_id: UUID,
    schema_in: SchemaUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a schema.
    """
    schema = await schema_crud.get(db, id=schema_id)
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schema not found",
        )
    
    # Check if user is the owner
    if str(schema.owner_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this schema",
        )
    
    # If name is being updated, check for conflicts
    if schema_in.name and schema_in.name != schema.name:
        existing_schema = await schema_crud.get_by_name_and_owner(
            db, name=schema_in.name, owner_id=current_user.id
        )
        if existing_schema and str(existing_schema.id) != str(schema_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A schema with this name already exists for this user.",
            )
    
    schema = await schema_crud.update(db, db_obj=schema, obj_in=schema_in)
    return schema

@router.delete("/{schema_id}", response_model=Schema)
async def delete_schema(
    *,
    db: AsyncSession = Depends(get_db),
    schema_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a schema.
    """
    schema = await schema_crud.get(db, id=schema_id)
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schema not found",
        )
    
    # Check if user is the owner
    if str(schema.owner_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this schema",
        )
    
    # Check if schema is used by any structures
    if hasattr(schema, 'structures') and len(schema.structures) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete schema that is being used by one or more structures",
        )
    
    schema = await schema_crud.remove(db, id=schema_id)
    return schema

@router.get("/{schema_id}/validate", response_model=dict)
async def validate_data_against_schema(
    *,
    db: AsyncSession = Depends(get_db),
    schema_id: UUID,
    data: dict,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Validate data against a schema.
    """
    schema = await schema_crud.get(db, id=schema_id)
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schema not found",
        )
    
    # Check if user has access to this schema
    if not schema.is_public and str(schema.owner_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # TODO: Implement schema validation logic
    # This is a placeholder for actual validation
    try:
        # Here you would validate the data against the schema definition
        # For now, we'll just return a success response
        return {
            "valid": True,
            "message": "Data is valid according to the schema",
            "schema_id": str(schema_id),
            "data": data
        }
    except Exception as e:
        return {
            "valid": False,
            "message": str(e),
            "schema_id": str(schema_id),
            "data": data
        }
