"""
Structure management API endpoints.
"""
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from ....core.security import get_current_active_user
from ....crud.crud_structure import structure_crud
from ....db.deps import get_db
from ....models.structure import Structure, StructureCreate, StructureUpdate, StructureInDB
from ....models.user import User
from ....schemas.msg import Msg

router = APIRouter()

@router.get("/", response_model=List[Structure])
async def read_structures(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve structures. Returns user's structures plus public ones.
    """
    structures = await structure_crud.get_multi_by_owner(
        db, owner_id=current_user.id, skip=skip, limit=limit, include_public=True
    )
    return structures

@router.post("/", response_model=Structure)
async def create_structure(
    *,
    db: AsyncSession = Depends(get_db),
    structure_in: StructureCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new structure.
    """
    # Check if structure with this name already exists for the user
    existing_structure = await structure_crud.get_by_name_and_owner(
        db, name=structure_in.name, owner_id=current_user.id
    )
    if existing_structure:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A structure with this name already exists for this user.",
        )
    
    # If schema_id is provided, verify it exists and user has access
    if structure_in.schema_id:
        from ....crud.crud_schema import schema_crud
        schema = await schema_crud.get(db, id=structure_in.schema_id)
        if not schema:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schema with ID {structure_in.schema_id} not found",
            )
        if not schema.is_public and str(schema.owner_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to use this schema",
            )
    
    structure = await structure_crud.create_with_owner(
        db, obj_in=structure_in, owner_id=current_user.id
    )
    return structure

@router.get("/public", response_model=List[Structure])
async def read_public_structures(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve public structures.
    """
    structures = await structure_crud.get_public_structures(db, skip=skip, limit=limit)
    return structures

@router.get("/{structure_id}", response_model=Structure)
async def read_structure(
    structure_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get structure by ID.
    """
    structure = await structure_crud.get(db, id=structure_id)
    if not structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Structure not found",
        )
    
    # Check if user has access to this structure
    if not structure.is_public and str(structure.owner_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return structure

@router.put("/{structure_id}", response_model=Structure)
async def update_structure(
    *,
    db: AsyncSession = Depends(get_db),
    structure_id: UUID,
    structure_in: StructureUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a structure.
    """
    structure = await structure_crud.get(db, id=structure_id)
    if not structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Structure not found",
        )
    
    # Check if user is the owner
    if str(structure.owner_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this structure",
        )
    
    # If name is being updated, check for conflicts
    if structure_in.name and structure_in.name != structure.name:
        existing_structure = await structure_crud.get_by_name_and_owner(
            db, name=structure_in.name, owner_id=current_user.id
        )
        if existing_structure and str(existing_structure.id) != str(structure_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A structure with this name already exists for this user.",
            )
    
    # If schema_id is being updated, verify the new schema exists and user has access
    if structure_in.schema_id is not None and structure_in.schema_id != structure.schema_id:
        from ....crud.crud_schema import schema_crud
        schema = await schema_crud.get(db, id=structure_in.schema_id)
        if not schema:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schema with ID {structure_in.schema_id} not found",
            )
        if not schema.is_public and str(schema.owner_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to use this schema",
            )
    
    structure = await structure_crud.update(db, db_obj=structure, obj_in=structure_in)
    return structure

@router.delete("/{structure_id}", response_model=Structure)
async def delete_structure(
    *,
    db: AsyncSession = Depends(get_db),
    structure_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a structure.
    """
    structure = await structure_crud.get(db, id=structure_id)
    if not structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Structure not found",
        )
    
    # Check if user is the owner
    if str(structure.owner_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this structure",
        )
    
    # Check if structure contains any data items
    if hasattr(structure, 'items') and len(structure.items) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete structure that contains data items",
        )
    
    structure = await structure_crud.remove(db, id=structure_id)
    return structure

@router.get("/{structure_id}/stats", response_model=dict)
async def get_structure_stats(
    *,
    db: AsyncSession = Depends(get_db),
    structure_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get statistics for a structure.
    """
    structure = await structure_crud.get(db, id=structure_id)
    if not structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Structure not found",
        )
    
    # Check if user has access to this structure
    if not structure.is_public and str(structure.owner_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Get item count
    item_count = len(structure.items) if hasattr(structure, 'items') else 0
    
    # Get status distribution
    status_dist = {}
    if hasattr(structure, 'items') and structure.items:
        for item in structure.items:
            status_dist[item.status] = status_dist.get(item.status, 0) + 1
    
    # Get last updated timestamp
    last_updated = None
    if hasattr(structure, 'items') and structure.items:
        last_updated = max(
            item.updated_at or item.created_at 
            for item in structure.items
            if item.updated_at or item.created_at
        )
    
    return {
        "structure_id": str(structure_id),
        "name": structure.name,
        "item_count": item_count,
        "status_distribution": status_dist,
        "created_at": structure.created_at.isoformat() if structure.created_at else None,
        "updated_at": structure.updated_at.isoformat() if structure.updated_at else None,
        "last_updated": last_updated.isoformat() if last_updated else None,
    }
