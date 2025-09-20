"""
Edix - Universal Data Structure Editor

A powerful editor for managing data structures with dynamic SQL table creation,
built-in frontend, and integration capabilities with existing projects.
"""

__version__ = "0.1.0"

# Main application imports
from .app import app, run_server

# Re-export commonly used components
from .models import Structure, DataItem, Schema
from .database import DatabaseManager
from .schemas import SchemaManager

__all__ = [
    'app',
    'run_server',
    'Structure',
    'DataItem',
    'Schema',
    'DatabaseManager',
    'SchemaManager'
]
