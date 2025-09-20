"""
Database dependencies for FastAPI routes.
"""
from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .base import get_db, AsyncSessionLocal

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function that yields database sessions.
    
    This is the main dependency that should be used in route handlers.
    
    Example:
        @router.get("/items/{item_id}")
        async def read_item(
            item_id: int, 
            db: AsyncSession = Depends(get_db_session)
        ):
            item = await db.get(Item, item_id)
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            return item
    """
    async for session in get_db():
        yield session

async def get_db_session_transaction() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session within a transaction.
    
    Automatically commits on success or rolls back on exception.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

# Type alias for dependency injection
DatabaseSession = Depends(get_db_session)
DatabaseTransaction = Depends(get_db_session_transaction)
