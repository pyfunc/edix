"""
Database management for Edix
"""
import json
import sqlite3
import aiosqlite
from pathlib import Path
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, db_path: str = "edix.db"):
        """Initialize database manager"""
        self.db_path = db_path
        self.conn: Optional[aiosqlite.Connection] = None
        
    async def initialize(self):
        """Initialize database connection and create tables"""
        # Create directory if it doesn't exist
        db_path = Path(self.db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = await aiosqlite.connect(self.db_path)
        self.conn.row_factory = aiosqlite.Row  # Enable column access by name
        
        # Enable foreign keys
        await self.conn.execute("PRAGMA foreign_keys = ON")
        await self.conn.commit()
        
        # Create metadata tables
        await self._create_metadata_tables()
    
    async def _create_metadata_tables(self):
        """Create system metadata tables"""
        tables = ["""
        CREATE TABLE IF NOT EXISTS schemas (
            name TEXT PRIMARY KEY,
            definition TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """, """
        CREATE TABLE IF NOT EXISTS structures (
            name TEXT PRIMARY KEY,
            schema_name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (schema_name) REFERENCES schemas(name) ON DELETE CASCADE
        )
        """]
        
        for table_sql in tables:
            await self.conn.execute(table_sql)
        
        await self.conn.commit()
    
    async def create_table_from_schema(self, schema_name: str, schema_definition: dict):
        """Create a new table based on a schema"""
        if not self.conn:
            raise RuntimeError("Database not initialized")
            
        table_name = f"data_{schema_name}"
        fields = schema_definition.get("fields", {})
        
        # Start building the SQL
        columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
        
        # Add fields as columns
        for field_name, field_def in fields.items():
            sql_type = self._get_sql_type(field_def["type"])
            nullable = " NOT NULL" if field_def.get("required", True) else ""
            columns.append(f"{field_name} {sql_type}{nullable}")
        
        # Add timestamps
        columns.extend([
            "created_at TEXT NOT NULL",
            "updated_at TEXT NOT NULL"
        ])
        
        # Create the table
        create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
        await self.conn.execute(create_sql)
        
        # Create indexes
        for index_fields in schema_definition.get("indexes", []):
            index_name = f"idx_{schema_name}_" + "_".join(index_fields)
            index_sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({', '.join(index_fields)})"
            await self.conn.execute(index_sql)
        
        await self.conn.commit()
    
    def _get_sql_type(self, field_type: str) -> str:
        """Map field type to SQL type"""
        type_map = {
            "string": "TEXT",
            "integer": "INTEGER",
            "float": "REAL",
            "boolean": "INTEGER",  # SQLite doesn't have boolean
            "datetime": "TEXT",
            "date": "TEXT",
            "time": "TEXT",
            "json": "TEXT"
        }
        return type_map.get(field_type.lower(), "TEXT")
    
    async def insert_data(self, schema_name: str, data: Dict[str, Any]) -> int:
        """Insert data into a schema table"""
        if not self.conn:
            raise RuntimeError("Database not initialized")
            
        table_name = f"data_{schema_name}"
        now = datetime.utcnow().isoformat()
        
        # Prepare data
        data["created_at"] = now
        data["updated_at"] = now
        
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        values = list(data.values())
        
        query = f"""
        INSERT INTO {table_name} ({columns})
        VALUES ({placeholders})
        """
        
        cursor = await self.conn.execute(query, values)
        await self.conn.commit()
        return cursor.lastrowid
    
    async def update_data(self, schema_name: str, item_id: int, data: Dict[str, Any]) -> bool:
        """Update data in a schema table"""
        if not self.conn:
            raise RuntimeError("Database not initialized")
            
        table_name = f"data_{schema_name}"
        now = datetime.utcnow().isoformat()
        
        # Prepare data
        data["updated_at"] = now
        
        set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
        values = list(data.values())
        values.append(item_id)  # For the WHERE clause
        
        query = f"""
        UPDATE {table_name}
        SET {set_clause}
        WHERE id = ?
        """
        
        cursor = await self.conn.execute(query, values)
        await self.conn.commit()
        return cursor.rowcount > 0
    
    async def delete_data(self, schema_name: str, item_id: int) -> bool:
        """Delete data from a schema table"""
        if not self.conn:
            raise RuntimeError("Database not initialized")
            
        table_name = f"data_{schema_name}"
        
        query = f"""
        DELETE FROM {table_name}
        WHERE id = ?
        """
        
        cursor = await self.conn.execute(query, (item_id,))
        await self.conn.commit()
        return cursor.rowcount > 0
    
    async def get_data(self, schema_name: str, item_id: int) -> Optional[Dict[str, Any]]:
        """Get a single item from a schema table"""
        if not self.conn:
            raise RuntimeError("Database not initialized")
            
        table_name = f"data_{schema_name}"
        
        query = f"""
        SELECT * FROM {table_name}
        WHERE id = ?
        """
        
        cursor = await self.conn.execute(query, (item_id,))
        row = await cursor.fetchone()
        
        if not row:
            return None
            
        return dict(row)
    
    async def list_data(
        self, 
        schema_name: str, 
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List data from a schema table with optional filtering"""
        if not self.conn:
            raise RuntimeError("Database not initialized")
            
        table_name = f"data_{schema_name}"
        
        # Build WHERE clause
        where_clause = ""
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"{key} = ?")
                params.append(value)
            where_clause = "WHERE " + " AND ".join(conditions)
        
        query = f"""
        SELECT * FROM {table_name}
        {where_clause}
        ORDER BY updated_at DESC
        LIMIT ? OFFSET ?
        """
        
        params.extend([limit, offset])
        
        cursor = await self.conn.execute(query, params)
        rows = await cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    async def close(self):
        """Close the database connection"""
        if self.conn:
            await self.conn.close()
            self.conn = None
