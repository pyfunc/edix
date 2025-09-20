"""
Database manager with dynamic table creation
"""
import json
import yaml
import csv
import io
from typing import Dict, Any, List, Optional
from pathlib import Path
import aiosqlite
from datetime import datetime


class DatabaseManager:
    """Dynamic SQLite database manager"""
    
    def __init__(self, db_path: str = "edix.db"):
        self.db_path = db_path
        self.connection = None
        
    async def initialize(self):
        """Initialize database with system tables"""
        self.connection = await aiosqlite.connect(self.db_path)
        self.connection.row_factory = aiosqlite.Row
        
        # Create system tables
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS edix_structures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                schema TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                meta JSON
            )
        """)
        
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS edix_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                structure_name TEXT NOT NULL,
                version INTEGER NOT NULL,
                migration TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await self.connection.commit()
    
    async def close(self):
        """Close database connection"""
        if self.connection:
            await self.connection.close()
    
    def _get_sql_type(self, json_type: str, constraints: Dict = None) -> str:
        """Convert JSON schema type to SQL type"""
        type_mapping = {
            "string": "TEXT",
            "number": "REAL",
            "integer": "INTEGER",
            "boolean": "INTEGER",  # 0 or 1
            "array": "JSON",
            "object": "JSON",
            "null": "TEXT"
        }
        
        sql_type = type_mapping.get(json_type, "TEXT")
        
        # Add constraints
        if constraints:
            if constraints.get("maxLength") and json_type == "string":
                sql_type = f"VARCHAR({constraints['maxLength']})"
            
        return sql_type
    
    async def create_table_from_schema(self, table_name: str, schema: Dict[str, Any]):
        """Create SQL table from JSON schema"""
        
        # Sanitize table name
        safe_table_name = f"edix_data_{table_name.lower().replace('-', '_')}"
        
        # Parse schema properties
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        
        # Build CREATE TABLE statement
        columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
        
        for prop_name, prop_schema in properties.items():
            # Sanitize column name
            safe_col_name = prop_name.lower().replace("-", "_")
            
            # Get SQL type
            sql_type = self._get_sql_type(
                prop_schema.get("type", "string"),
                prop_schema
            )
            
            # Check if required
            if prop_name in required:
                sql_type += " NOT NULL"
            
            # Add default value if specified
            if "default" in prop_schema:
                default_value = prop_schema["default"]
                if isinstance(default_value, str):
                    sql_type += f" DEFAULT '{default_value}'"
                else:
                    sql_type += f" DEFAULT {default_value}"
            
            columns.append(f"{safe_col_name} {sql_type}")
        
        # Add metadata columns
        columns.extend([
            "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "_meta JSON"
        ])
        
        # Create table
        create_sql = f"""
            CREATE TABLE IF NOT EXISTS {safe_table_name} (
                {', '.join(columns)}
            )
        """
        
        await self.connection.execute(create_sql)
        
        # Create indexes for searchable fields
        for prop_name, prop_schema in properties.items():
            if prop_schema.get("index", False):
                safe_col_name = prop_name.lower().replace("-", "_")
                index_name = f"idx_{safe_table_name}_{safe_col_name}"
                await self.connection.execute(
                    f"CREATE INDEX IF NOT EXISTS {index_name} ON {safe_table_name} ({safe_col_name})"
                )
        
        await self.connection.commit()
        
        # Save structure definition
        await self.connection.execute("""
            INSERT OR REPLACE INTO edix_structures (name, schema, meta)
            VALUES (?, ?, ?)
        """, (
            table_name,
            json.dumps(schema),
            json.dumps({"table_name": safe_table_name})
        ))
        
        await self.connection.commit()
    
    async def list_structures(self) -> List[Dict[str, Any]]:
        """List all registered structures"""
        cursor = await self.connection.execute(
            "SELECT * FROM edix_structures ORDER BY name"
        )
        rows = await cursor.fetchall()
        
        structures = []
        for row in rows:
            structures.append({
                "id": row["id"],
                "name": row["name"],
                "schema": json.loads(row["schema"]),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "meta": json.loads(row["meta"]) if row["meta"] else {}
            })
        
        return structures
    
    async def get_structure_schema(self, structure_name: str) -> Dict[str, Any]:
        """Get schema for a structure"""
        cursor = await self.connection.execute(
            "SELECT schema FROM edix_structures WHERE name = ?",
            (structure_name,)
        )
        row = await cursor.fetchone()
        
        if not row:
            raise ValueError(f"Structure '{structure_name}' not found")
        
        return json.loads(row["schema"])
    
    async def get_structure_data(self, structure_name: str) -> List[Dict[str, Any]]:
        """Get all data for a structure"""
        # Get table name
        cursor = await self.connection.execute(
            "SELECT meta FROM edix_structures WHERE name = ?",
            (structure_name,)
        )
        row = await cursor.fetchone()
        
        if not row:
            raise ValueError(f"Structure '{structure_name}' not found")
        
        meta = json.loads(row["meta"])
        table_name = meta.get("table_name")
        
        # Get data
        cursor = await self.connection.execute(f"SELECT * FROM {table_name}")
        rows = await cursor.fetchall()
        
        data = []
        for row in rows:
            item = dict(row)
            # Parse JSON fields
            if "_meta" in item and item["_meta"]:
                item["_meta"] = json.loads(item["_meta"])
            data.append(item)
        
        return data
    
    async def insert_data(
        self,
        structure_name: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Insert data into structure table"""
        # Get table name and schema
        cursor = await self.connection.execute(
            "SELECT schema, meta FROM edix_structures WHERE name = ?",
            (structure_name,)
        )
        row = await cursor.fetchone()
        
        if not row:
            raise ValueError(f"Structure '{structure_name}' not found")
        
        schema = json.loads(row["schema"])
        meta = json.loads(row["meta"])
        table_name = meta.get("table_name")
        
        # Prepare data for insertion
        columns = []
        values = []
        placeholders = []
        
        for key, value in data.items():
            safe_col_name = key.lower().replace("-", "_")
            columns.append(safe_col_name)
            
            # Convert complex types to JSON
            if isinstance(value, (dict, list)):
                values.append(json.dumps(value))
            else:
                values.append(value)
            
            placeholders.append("?")
        
        # Add metadata
        columns.append("_meta")
        values.append(json.dumps(data.get("_meta", {})))
        placeholders.append("?")
        
        # Insert data
        insert_sql = f"""
            INSERT INTO {table_name} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
        """
        
        cursor = await self.connection.execute(insert_sql, values)
        await self.connection.commit()
        
        return {"id": cursor.lastrowid}
    
    async def update_data(
        self,
        structure_name: str,
        item_id: int,
        data: Dict[str, Any]
    ):
        """Update data in structure table"""
        # Get table name
        cursor = await self.connection.execute(
            "SELECT meta FROM edix_structures WHERE name = ?",
            (structure_name,)
        )
        row = await cursor.fetchone()
        
        if not row:
            raise ValueError(f"Structure '{structure_name}' not found")
        
        meta = json.loads(row["meta"])
        table_name = meta.get("table_name")
        
        # Prepare update statement
        set_clauses = []
        values = []
        
        for key, value in data.items():
            if key != "id":  # Don't update ID
                safe_col_name = key.lower().replace("-", "_")
                set_clauses.append(f"{safe_col_name} = ?")
                
                # Convert complex types to JSON
                if isinstance(value, (dict, list)):
                    values.append(json.dumps(value))
                else:
                    values.append(value)
        
        # Add updated_at
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        
        # Add ID for WHERE clause
        values.append(item_id)
        
        # Update data
        update_sql = f"""
            UPDATE {table_name}
            SET {', '.join(set_clauses)}
            WHERE id = ?
        """
        
        await self.connection.execute(update_sql, values)
        await self.connection.commit()
    
    async def delete_data(self, structure_name: str, item_id: int):
        """Delete data from structure table"""
        # Get table name
        cursor = await self.connection.execute(
            "SELECT meta FROM edix_structures WHERE name = ?",
            (structure_name,)
        )
        row = await cursor.fetchone()
        
        if not row:
            raise ValueError(f"Structure '{structure_name}' not found")
        
        meta = json.loads(row["meta"])
        table_name = meta.get("table_name")
        
        # Delete data
        await self.connection.execute(
            f"DELETE FROM {table_name} WHERE id = ?",
            (item_id,)
        )
        await self.connection.commit()
    
    async def export_structure(self, structure_name: str, format: str) -> Any:
        """Export structure data in specified format"""
        data = await self.get_structure_data(structure_name)
        
        if format == "json":
            return data
        elif format == "yaml":
            return yaml.dump(data, allow_unicode=True)
        elif format == "csv":
            if not data:
                return ""
            
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
            return output.getvalue()
        elif format == "xml":
            # Simple XML export
            from xml.etree.ElementTree import Element, SubElement, tostring
            root = Element("data")
            for item in data:
                record = SubElement(root, "record")
                for key, value in item.items():
                    field = SubElement(record, key)
                    field.text = str(value)
            return tostring(root, encoding="unicode")
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    async def import_data(self, format: str, data: Any) -> Dict[str, int]:
        """Import data from specified format"""
        if format == "json":
            items = data if isinstance(data, list) else [data]
        elif format == "yaml":
            items = yaml.safe_load(data)
            items = items if isinstance(items, list) else [items]
        elif format == "csv":
            reader = csv.DictReader(io.StringIO(data))
            items = list(reader)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        count = 0
        for item in items:
            structure_name = item.pop("_structure", "default")
            await self.insert_data(structure_name, item)
            count += 1
        
        return {"count": count}
    
    async def save_structure(self, structure):
        """Save structure definition"""
        await self.connection.execute("""
            INSERT OR REPLACE INTO edix_structures (name, schema, meta)
            VALUES (?, ?, ?)
        """, (
            structure.name,
            json.dumps(structure.schema),
            json.dumps(structure.meta or {})
        ))
        await self.connection.commit()