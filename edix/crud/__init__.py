"""
CRUD operations for the application.

This module provides CRUD (Create, Read, Update, Delete) operations for all models
in the application. Each model has its own CRUD class that inherits from either
CRUDBase or CRUDBaseWithOwner.
"""
from .base import CRUDBase, CRUDBaseWithOwner
from .crud_user import user_crud, CRUDUser
from .crud_schema import schema_crud, CRUDSchema
from .crud_structure import structure_crud, CRUDStructure
from .crud_data_item import data_item_crud, CRUDDataItem

__all__ = [
    # Base classes
    "CRUDBase",
    "CRUDBaseWithOwner",
    
    # User CRUD
    "user_crud",
    "CRUDUser",
    
    # Schema CRUD
    "schema_crud",
    "CRUDSchema",
    
    # Structure CRUD
    "structure_crud",
    "CRUDStructure",
    
    # Data Item CRUD
    "data_item_crud",
    "CRUDDataItem",
]
