"""
User-related Pydantic models for request/response validation.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator

from .base import (
    BaseSchema, BaseCreateSchema, BaseUpdateSchema, 
    BaseInDBSchema, BaseResponseSchema
)

class UserBase(BaseSchema):
    """Base user schema with common fields."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: bool = True
    is_superuser: bool = False
    
    @validator('username')
    def username_must_be_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v

class UserCreate(UserBase, BaseCreateSchema):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8)
    
    class Config(UserBase.Config):
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "password": "securepassword123",
                "is_active": True,
                "is_superuser": False
            }
        }

class UserUpdate(BaseUpdateSchema):
    """Schema for updating an existing user."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    
    @validator('username')
    def username_must_be_alphanumeric(cls, v):
        if v is not None and not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "newemail@example.com",
                "username": "newusername",
                "full_name": "New Name",
                "password": "newsecurepassword123"
            }
        }

class UserInDB(UserBase, BaseInDBSchema):
    """User schema as stored in the database."""
    hashed_password: str
    
    class Config(UserBase.Config):
        pass

class UserResponse(UserBase, BaseResponseSchema):
    """User schema for API responses."""
    pass

class UserLogin(BaseModel):
    """Schema for user login."""
    username: str
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "password": "securepassword123"
            }
        }

class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }

class TokenData(BaseModel):
    """Schema for token data."""
    username: Optional[str] = None
    user_id: Optional[int] = None
    scopes: List[str] = []
