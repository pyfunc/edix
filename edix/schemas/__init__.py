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
    Schema, SchemaCreate, SchemaUpdate, SchemaInDB, SchemaResponse
)
from .structure import (
    Structure, StructureCreate, StructureUpdate, StructureInDB, StructureResponse
)
from .data_item import (
    DataItem, DataItemCreate, DataItemUpdate, DataItemInDB, DataItemResponse
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
    'Schema', 'SchemaCreate', 'SchemaUpdate', 'SchemaInDB', 'SchemaResponse',
    
    # Structure schemas
    'Structure', 'StructureCreate', 'StructureUpdate', 'StructureInDB', 'StructureResponse',
    
    # DataItem schemas
    'DataItem', 'DataItemCreate', 'DataItemUpdate', 'DataItemInDB', 'DataItemResponse',
    
    # Manager
    'SchemaManager',
]
