"""
Schema management for Edix data structures.

This module provides Pydantic models for data validation and serialization,
as well as the SchemaManager class for handling schema operations.
"""
from typing import Dict, Any, Optional, List, Type, TypeVar
from pydantic import BaseModel, Field, validator
from enum import Enum
import json

# Re-export all schema models for easier imports
from .base import (
    BaseSchema, BaseCreateSchema, BaseUpdateSchema, 
    BaseInDBSchema, BaseResponseSchema
)
from .user import (
    UserBase, UserCreate, UserUpdate, UserInDB, UserResponse,
    UserLogin, Token, TokenData
)
from .schema import (
    SchemaBase, SchemaCreate, SchemaUpdate, SchemaInDB, SchemaResponse,
    SchemaValidationError, SchemaValidationResult
)
from .structure import (
    StructureBase, StructureCreate, StructureUpdate, StructureInDB, StructureResponse,
    StructureType, StructureStatus
)
from .data_item import (
    DataItemBase, DataItemCreate, DataItemUpdate, DataItemInDB, DataItemResponse,
    BulkDataItemCreate, DataItemSearch, DataItemStatus
)

# Export SchemaManager
from .manager import SchemaManager

__all__ = [
    # Base schemas
    'BaseSchema', 'BaseCreateSchema', 'BaseUpdateSchema',
    'BaseInDBSchema', 'BaseResponseSchema',
    
    # User schemas
    'UserBase', 'UserCreate', 'UserUpdate', 'UserInDB', 'UserResponse',
    'UserLogin', 'Token', 'TokenData',
    
    # Schema schemas
    'SchemaBase', 'SchemaCreate', 'SchemaUpdate', 'SchemaInDB', 'SchemaResponse',
    'SchemaValidationError', 'SchemaValidationResult',
    
    # Structure schemas
    'StructureBase', 'StructureCreate', 'StructureUpdate', 'StructureInDB', 'StructureResponse',
    'StructureType', 'StructureStatus',
    
    # DataItem schemas
    'DataItemBase', 'DataItemCreate', 'DataItemUpdate', 'DataItemInDB', 'DataItemResponse',
    'BulkDataItemCreate', 'DataItemSearch', 'DataItemStatus',
    
    # Manager
    'SchemaManager',
]
