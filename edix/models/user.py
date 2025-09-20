"""
User model and related functionality.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field, validator
from sqlalchemy import Boolean, Column, DateTime, String, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base, BaseCRUD
from ..core.security import get_password_hash, verify_password

# Pydantic models
class UserBase(BaseModel):
    """Base user model with common attributes."""
    email: EmailStr = Field(..., description="User's email address")
    full_name: Optional[str] = Field(None, description="User's full name")
    is_active: bool = Field(True, description="Whether the user is active")
    is_superuser: bool = Field(False, description="Whether the user is a superuser")
    preferences: Optional[dict] = Field(
        None, 
        description="User preferences stored as JSON"
    )

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "full_name": "John Doe",
                "is_active": True,
                "is_superuser": False,
                "preferences": {"theme": "light"}
            }
        }

class UserCreate(UserBase):
    """Model for creating a new user."""
    password: str = Field(..., min_length=8, description="User's password")
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
                "full_name": "John Doe",
                "is_active": True,
                "is_superuser": False,
                "preferences": {"theme": "light"}
            }
        }

class UserUpdate(UserBase):
    """Model for updating an existing user."""
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, description="New password")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "new.email@example.com",
                "password": "newsecurepassword123",
                "full_name": "John Updated",
                "is_active": True,
                "preferences": {"theme": "dark"}
            }
        }

class UserInDBBase(UserBase):
    """Base model for user stored in database."""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class User(UserInDBBase):
    """User model for API responses."""
    pass

class UserInDB(UserInDBBase):
    """User model with hashed password for database storage."""
    hashed_password: str

# SQLAlchemy model
class DBUser(Base):
    """SQLAlchemy user model."""
    __tablename__ = "users"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    preferences = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    structures = relationship("DBStructure", back_populates="owner", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"
    
    def set_password(self, password: str):
        """Set the user's password."""
        self.hashed_password = get_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash."""
        return verify_password(password, self.hashed_password)

# CRUD operations
class UserCRUD(BaseCRUD[DBUser, UserCreate, UserUpdate]):
    """CRUD operations for users."""
    
    async def get_by_email(self, db, *, email: str) -> Optional[DBUser]:
        """Get a user by email."""
        return db.query(self.model).filter(self.model.email == email).first()
    
    async def create(self, db, *, obj_in: UserCreate) -> DBUser:
        """Create a new user with hashed password."""
        db_obj = self.model(
            email=obj_in.email,
            full_name=obj_in.full_name,
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
            preferences=obj_in.preferences
        )
        db_obj.set_password(obj_in.password)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    async def update(
        self, db, *, db_obj: DBUser, obj_in: UserUpdate
    ) -> DBUser:
        """Update a user, including password if provided."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        if "password" in update_data and update_data["password"]:
            db_obj.set_password(update_data["password"])
            del update_data["password"]
        
        return await super().update(db, db_obj=db_obj, obj_in=update_data)
    
    async def authenticate(
        self, db, *, email: str, password: str
    ) -> Optional[DBUser]:
        """Authenticate a user."""
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not user.check_password(password):
            return None
        return user
