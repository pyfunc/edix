"""
CRUD operations for User model.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..core.security import get_password_hash, verify_password
from ..models.user import User, UserCreate, UserInDB, UserUpdate
from .base import CRUDBase

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """
    CRUD operations for User model with additional authentication methods.
    """
    
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """Get a user by email."""
        result = await db.execute(
            select(self.model).where(self.model.email == email)
        )
        return result.scalars().first()
    
    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        """Create a new user with hashed password."""
        # Create a UserInDB instance to handle password hashing
        user_data = obj_in.dict()
        password = user_data.pop("password")
        user_data["hashed_password"] = get_password_hash(password)
        
        # Set timestamps
        now = datetime.utcnow()
        user_data["created_at"] = now
        user_data["updated_at"] = now
        
        # Create the user
        db_obj = self.model(**user_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self, db: AsyncSession, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """Update a user, handling password updates specially."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        # Handle password update
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            update_data["hashed_password"] = hashed_password
            del update_data["password"]
        
        # Update timestamps
        update_data["updated_at"] = datetime.utcnow()
        
        return await super().update(db, db_obj=db_obj, obj_in=update_data)
    
    async def authenticate(
        self, db: AsyncSession, *, email: str, password: str
    ) -> Optional[User]:
        """Authenticate a user by email and password."""
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    async def is_active(self, user: User) -> bool:
        """Check if a user is active."""
        return user.is_active
    
    async def is_superuser(self, user: User) -> bool:
        """Check if a user is a superuser."""
        return user.is_superuser

# Create a singleton instance
user_crud = CRUDUser(User)
