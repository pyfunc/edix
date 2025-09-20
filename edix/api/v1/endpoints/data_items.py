"""
Data items API endpoints.
"""
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from ....core.security import get_current_active_user
from ....crud.crud_data_item import data_item_crud
from ....crud.crud_structure import structure_crud
from ....db.deps import get_db
from ....models.data_item import DataItem, DataItemCreate, DataItemUpdate, DataItemInDB
from ....models.structure import Structure
from ....models.user import User
from ....schemas.msg import Msg

router = APIRouter()

def validate_data_item_access(
    structure: Structure, 
    current_user: User, 
    require_owner: bool = False
) -> None:
    """
    Validate that the current user has access to the data item's structure.
    """
    if not structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Structure not found",
        )
    
    # Check if user has access to this structure
    if not structure.is_public and str(structure.owner_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this structure",
        )
    
    # If require_owner is True, check if user is the owner
    if require_owner and str(structure.owner_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to modify this structure's data",
        )

@router.get("/", response_model=List[DataItem])
async def read_data_items(
    db: AsyncSession = Depends(get_db),
    structure_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve data items. Can be filtered by structure_id and status.
    """
    if structure_id:
        # Get items for a specific structure
        structure = await structure_crud.get(db, id=structure_id)
        validate_data_item_access(structure, current_user)
        
        items = await data_item_crud.get_multi_by_structure(
            db, 
            structure_id=structure_id, 
            skip=skip, 
            limit=limit,
            status=status
        )
    else:
        # Get all items for the current user
        items = await data_item_crud.get_multi_by_owner(
            db, 
            owner_id=current_user.id, 
            skip=skip, 
            limit=limit
        )
    
    return items

@router.post("/", response_model=DataItem)
async def create_data_item(
    *,
    db: AsyncSession = Depends(get_db),
    data_item_in: DataItemCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new data item.
    """
    # Verify the structure exists and user has access
    structure = await structure_crud.get(db, id=data_item_in.structure_id)
    validate_data_item_access(structure, current_user, require_owner=True)
    
    # If the structure has a schema, validate the data against it
    if structure.schema_id:
        from ....crud.crud_schema import schema_crud
        from ....api.v1.endpoints.schemas import validate_data_against_schema
        
        schema = await schema_crud.get(db, id=structure.schema_id)
        if schema:
            # This is a simplified validation - in a real app, you'd want more robust validation
            validation = await validate_data_against_schema(
                db=db,
                schema_id=schema.id,
                data=data_item_in.data,
                current_user=current_user
            )
            if not validation.get("valid"):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={
                        "message": "Data validation failed against schema",
                        "errors": validation.get("errors", []),
                    },
                )
    
    # Create the data item
    data_item = await data_item_crud.create_with_owner(
        db, 
        obj_in=data_item_in, 
        owner_id=current_user.id,
        structure_id=data_item_in.structure_id
    )
    
    return data_item

@router.get("/{item_id}", response_model=DataItem)
async def read_data_item(
    item_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get data item by ID.
    """
    data_item = await data_item_crud.get(db, id=item_id)
    if not data_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data item not found",
        )
    
    # Verify the structure exists and user has access
    structure = await structure_crud.get(db, id=data_item.structure_id)
    validate_data_item_access(structure, current_user)
    
    return data_item

@router.put("/{item_id}", response_model=DataItem)
async def update_data_item(
    *,
    db: AsyncSession = Depends(get_db),
    item_id: UUID,
    data_item_in: DataItemUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a data item.
    """
    data_item = await data_item_crud.get(db, id=item_id)
    if not data_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data item not found",
        )
    
    # Verify the structure exists and user has write access
    structure = await structure_crud.get(db, id=data_item.structure_id)
    validate_data_item_access(structure, current_user, require_owner=True)
    
    # If data is being updated, validate against the schema if one exists
    if data_item_in.data is not None and structure.schema_id:
        from ....crud.crud_schema import schema_crud
        from ....api.v1.endpoints.schemas import validate_data_against_schema
        
        schema = await schema_crud.get(db, id=structure.schema_id)
        if schema:
            # This is a simplified validation - in a real app, you'd want more robust validation
            validation = await validate_data_against_schema(
                db=db,
                schema_id=schema.id,
                data=data_item_in.data,
                current_user=current_user
            )
            if not validation.get("valid"):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={
                        "message": "Data validation failed against schema",
                        "errors": validation.get("errors", []),
                    },
                )
    
    data_item = await data_item_crud.update(db, db_obj=data_item, obj_in=data_item_in)
    return data_item

@router.delete("/{item_id}", response_model=DataItem)
async def delete_data_item(
    *,
    db: AsyncSession = Depends(get_db),
    item_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a data item.
    """
    data_item = await data_item_crud.get(db, id=item_id)
    if not data_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data item not found",
        )
    
    # Verify the structure exists and user has write access
    structure = await structure_crud.get(db, id=data_item.structure_id)
    validate_data_item_access(structure, current_user, require_owner=True)
    
    data_item = await data_item_crud.remove(db, id=item_id)
    return data_item

@router.get("/search/", response_model=List[DataItem])
async def search_data_items(
    *,
    db: AsyncSession = Depends(get_db),
    q: str,
    structure_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Search data items by query string.
    """
    if not q or len(q.strip()) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query must be at least 3 characters long",
        )
    
    if structure_id:
        # Verify the structure exists and user has access
        structure = await structure_crud.get(db, id=structure_id)
        validate_data_item_access(structure, current_user)
        
        items = await data_item_crud.search(
            db,
            query=q,
            structure_id=structure_id,
            skip=skip,
            limit=limit
        )
    else:
        # Search across all user's data items
        items = await data_item_crud.search(
            db,
            query=q,
            owner_id=current_user.id,
            skip=skip,
            limit=limit
        )
    
    return items

@router.post("/batch/", response_model=List[DataItem])
async def create_data_items_batch(
    *,
    db: AsyncSession = Depends(get_db),
    items_in: List[DataItemCreate],
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create multiple data items in a batch.
    """
    if not items_in:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No items provided",
        )
    
    # Group items by structure_id for batch validation
    structure_items = {}
    for item in items_in:
        if item.structure_id not in structure_items:
            structure_items[item.structure_id] = []
        structure_items[item.structure_id].append(item)
    
    # Validate all structures and check permissions
    for structure_id, items in structure_items.items():
        structure = await structure_crud.get(db, id=structure_id)
        validate_data_item_access(structure, current_user, require_owner=True)
        
        # If the structure has a schema, validate all items against it
        if structure.schema_id:
            from ....crud.crud_schema import schema_crud
            from ....api.v1.endpoints.schemas import validate_data_against_schema
            
            schema = await schema_crud.get(db, id=structure.schema_id)
            if schema:
                for item in items:
                    validation = await validate_data_against_schema(
                        db=db,
                        schema_id=schema.id,
                        data=item.data,
                        current_user=current_user
                    )
                    if not validation.get("valid"):
                        raise HTTPException(
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail={
                                "message": f"Data validation failed against schema for structure {structure_id}",
                                "structure_id": str(structure_id),
                                "errors": validation.get("errors", []),
                            },
                        )
    
    # Create all items
    created_items = []
    for item_in in items_in:
        item = await data_item_crud.create_with_owner(
            db, 
            obj_in=item_in, 
            owner_id=current_user.id,
            structure_id=item_in.structure_id
        )
        created_items.append(item)
    
    return created_items
