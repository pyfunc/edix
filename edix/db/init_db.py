"""
Database initialization and migration utilities.
"""
import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy_utils import create_database, database_exists, drop_database

from ...config import settings
from .base import Base, engine, init_db

logger = logging.getLogger(__name__)

async def create_tables() -> None:
    ""Create all database tables."""
    logger.info("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully.")

async def drop_tables() -> None:
    ""Drop all database tables."""
    logger.warning("Dropping all database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.warning("All database tables dropped.")

async def recreate_tables() -> None:
    ""Recreate all database tables (drop and create)."""
    await drop_tables()
    await create_tables()

async def check_database_connection() -> bool:
    ""Check if the database is accessible."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

async def get_database_version() -> Optional[str]:
    ""Get the current database version from the database."""
    try:
        async with engine.connect() as conn:
            # Check if the migrations table exists
            result = await conn.execute(
                text(
                    """
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='alembic_version'
                    """
                )
            )
            if result.scalar():
                # Get the current migration version
                result = await conn.execute(
                    text("SELECT version_num FROM alembic_version")
                )
                return result.scalar()
    except Exception as e:
        logger.warning(f"Could not determine database version: {e}")
    return None

async def initialize_database() -> None:
    ""Initialize the database with required tables and data."""
    logger.info("Initializing database...")
    
    # Check if database exists, create if not
    if not await database_exists(settings.database_url_async):
        logger.info("Creating database...")
        await create_database(settings.database_url_async)
    
    # Create tables
    await create_tables()
    
    # Check if we need to run migrations
    current_version = await get_database_version()
    if current_version is None:
        logger.info("No database version found, initializing...")
        # Add any initial data here if needed
    else:
        logger.info(f"Database version: {current_version}")
    
    logger.info("Database initialization complete.")

async def reset_database() -> None:
    ""Reset the database by dropping and recreating all tables."""
    logger.warning("Resetting database...")
    if await database_exists(settings.database_url_async):
        await drop_database(settings.database_url_async)
    await initialize_database()
    logger.info("Database reset complete.")

# For command-line usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database management commands")
    parser.add_argument(
        "--init", action="store_true", help="Initialize the database"
    )
    parser.add_argument(
        "--reset", action="store_true", help="Reset the database (DANGER: deletes all data)"
    )
    parser.add_argument(
        "--create-tables", action="store_true", help="Create all database tables"
    )
    parser.add_argument(
        "--drop-tables", action="store_true", help="Drop all database tables"
    )
    parser.add_argument(
        "--check", action="store_true", help="Check database connection"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    async def run():
        if args.init:
            await initialize_database()
        elif args.reset:
            await reset_database()
        elif args.create_tables:
            await create_tables()
        elif args.drop_tables:
            await drop_tables()
        elif args.check:
            if await check_database_connection():
                version = await get_database_version()
                print(f"✅ Database connection successful (version: {version or 'N/A'})")
            else:
                print("❌ Database connection failed")
        else:
            parser.print_help()
    
    asyncio.run(run())
