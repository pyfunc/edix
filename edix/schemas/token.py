"""
Token response schemas for authentication endpoints.
"""
from typing import Optional

from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    """
    JWT token response schema.
    
    Used for authentication token responses.
    """
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "refresh_token": "def50200..."
            }
        }
    )


class TokenPayload(BaseModel):
    """
    JWT token payload schema.
    
    Used for decoding JWT token contents.
    """
    sub: Optional[str] = None  # Subject (usually user ID or username)
    exp: Optional[int] = None  # Expiration time
    iat: Optional[int] = None  # Issued at time
    iss: Optional[str] = None  # Issuer
    aud: Optional[str] = None  # Audience
    scopes: Optional[list[str]] = None  # Access scopes
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sub": "user123",
                "exp": 1640995200,
                "iat": 1640908800,
                "iss": "edix-api",
                "aud": "edix-frontend",
                "scopes": ["read", "write"]
            }
        }
    )


class RefreshToken(BaseModel):
    """
    Refresh token request schema.
    
    Used for token refresh requests.
    """
    refresh_token: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "def50200..."
            }
        }
    )
