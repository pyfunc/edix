"""
Schema management for Edix data structures.

This module provides the SchemaManager class for handling schema operations
including validation, registration, and retrieval of schemas.
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union

import jsonschema
from jsonschema import Draft7Validator, ValidationError
from pydantic import BaseModel, ValidationError as PydanticValidationError

from . import SchemaBase, SchemaCreate, SchemaUpdate, SchemaInDB, SchemaResponse
from ..database import DatabaseManager
from ..db.base import AsyncSessionLocal
from ..models.schema import Schema as DBSchema
from ..crud import schema_crud

class SchemaManager:
    """
    Manages JSON schemas for data validation in the Edix application.
    
    This class handles the registration, validation, and management of JSON schemas
    that define the structure of data items in the application.
    """
    
    def __init__(self, db: DatabaseManager):
        """Initialize the SchemaManager with a database connection."""
        self.db = db
        self._schemas: Dict[str, dict] = {}
        self._validators: Dict[str, Draft7Validator] = {}
        self._schema_models: Dict[str, Type[BaseModel]] = {}
    
    async def load_schemas(self) -> None:
        """
        Load all schemas from the database into memory.
        
        This method should be called during application startup.
        """
        async with AsyncSessionLocal() as session:
            db_schemas = await schema_crud.get_multi(session)
            for schema in db_schemas:
                try:
                    self._schemas[schema.name] = schema.schema_definition
                    self._validators[schema.name] = Draft7Validator(schema.schema_definition)
                except Exception as e:
                    print(f"Error loading schema {schema.name}: {e}")
    
    async def register_schema(self, name: str, schema_definition: dict) -> SchemaInDB:
        """
        Register a new JSON schema.
        
        Args:
            name: The name of the schema
            schema_definition: The JSON schema definition
            
        Returns:
            The created schema
            
        Raises:
            ValueError: If the schema is invalid
        """
        # Validate the schema definition
        try:
            Draft7Validator.check_schema(schema_definition)
        except Exception as e:
            raise ValueError(f"Invalid JSON schema: {e}")
        
        # Create the schema in the database
        schema_in = SchemaCreate(
            name=name,
            description=schema_definition.get("description", ""),
            schema_definition=schema_definition,
            is_public=True
        )
        
        async with AsyncSessionLocal() as session:
            db_schema = await schema_crud.create(session, obj_in=schema_in)
            
            # Update in-memory cache
            self._schemas[name] = db_schema.schema_definition
            self._validators[name] = Draft7Validator(db_schema.schema_definition)
            
            return db_schema
    
    async def validate_data(
        self, 
        schema_name: str, 
        data: Union[dict, list], 
        raise_on_error: bool = True
    ) -> dict:
        """
        Validate data against a registered schema.
        
        Args:
            schema_name: The name of the schema to validate against
            data: The data to validate
            raise_on_error: Whether to raise an exception on validation error
            
        Returns:
            A dictionary with validation results
            
        Raises:
            ValueError: If the schema is not found or validation fails (if raise_on_error is True)
        """
        if schema_name not in self._validators:
            error_msg = f"Schema '{schema_name}' not found"
            if raise_on_error:
                raise ValueError(error_msg)
            return {
                "valid": False,
                "errors": [error_msg],
                "schema": schema_name
            }
        
        validator = self._validators[schema_name]
        errors = []
        
        try:
            validator.validate(data)
            return {
                "valid": True,
                "errors": [],
                "schema": schema_name
            }
        except ValidationError as e:
            errors = [str(error) for error in validator.iter_errors(data)]
            
            if raise_on_error:
                raise ValueError(f"Validation failed: {', '.join(errors)}")
                
            return {
                "valid": False,
                "errors": errors,
                "schema": schema_name
            }
    
    async def get_schema(self, name: str) -> Optional[dict]:
        """
        Get a schema by name.
        
        Args:
            name: The name of the schema
            
        Returns:
            The schema definition or None if not found
        """
        return self._schemas.get(name)
    
    async def list_schemas(self) -> List[str]:
        """
        List all registered schema names.
        
        Returns:
            A list of schema names
        """
        return list(self._schemas.keys())
    
    async def update_schema(
        self, 
        name: str, 
        schema_definition: dict,
        description: Optional[str] = None
    ) -> Optional[SchemaInDB]:
        """
        Update an existing schema.
        
        Args:
            name: The name of the schema to update
            schema_definition: The new schema definition
            description: Optional new description
            
        Returns:
            The updated schema or None if not found
            
        Raises:
            ValueError: If the new schema is invalid
        """
        # Validate the new schema definition
        try:
            Draft7Validator.check_schema(schema_definition)
        except Exception as e:
            raise ValueError(f"Invalid JSON schema: {e}")
        
        async with AsyncSessionLocal() as session:
            # Get the existing schema
            db_schema = await schema_crud.get_by_name(session, name=name)
            if not db_schema:
                return None
            
            # Update the schema
            update_data = {
                "schema_definition": schema_definition
            }
            if description is not None:
                update_data["description"] = description
                
            updated_schema = await schema_crud.update(
                session, 
                db_obj=db_schema, 
                obj_in=update_data
            )
            
            # Update in-memory cache
            self._schemas[name] = updated_schema.schema_definition
            self._validators[name] = Draft7Validator(updated_schema.schema_definition)
            
            return updated_schema
    
    async def delete_schema(self, name: str) -> bool:
        """
        Delete a schema by name.
        
        Args:
            name: The name of the schema to delete
            
        Returns:
            True if the schema was deleted, False if not found
        """
        async with AsyncSessionLocal() as session:
            db_schema = await schema_crud.get_by_name(session, name=name)
            if not db_schema:
                return False
                
            await schema_crud.remove(session, id=db_schema.id)
            
            # Update in-memory cache
            if name in self._schemas:
                del self._schemas[name]
            if name in self._validators:
                del self._validators[name]
                
            return True
