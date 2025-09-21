"""
Authentication API endpoints.
"""
from datetime import timedelta
from typing import Any, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ....config import settings
from ....core.security import (
    create_access_token,
    get_current_active_user,
    get_password_hash,
    verify_password,
)
from ....crud.crud_user import user_crud
from ....db.deps import get_db
from ....models.user import User, UserCreate, UserInDB, UserUpdate
from ....schemas.msg import Msg
from ....schemas.token import Token as TokenSchema

router = APIRouter()

@router.post("/login/access-token", response_model=TokenSchema)
async def login_access_token(
    db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await user_crud.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/login/test-token", response_model=User)
async def test_token(current_user: User = Depends(get_current_active_user)) -> Any:
    """
    Test access token
    """
    return current_user

@router.post("/register", response_model=User)
async def create_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Create new user.
    """
    user = await user_crud.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
    
    user = await user_crud.create(db, obj_in=user_in)
    return user

@router.get("/me", response_model=User)
async def read_user_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.put("/me", response_model=User)
async def update_user_me(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    user = await user_crud.update(db, db_obj=current_user, obj_in=user_in)
    return user

@router.post("/password-recovery/{email}", response_model=Msg)
async def recover_password(email: str, db: AsyncSession = Depends(get_db)) -> Any:
    """
    Password Recovery
    """
    user = await user_crud.get_by_email(db, email=email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this email does not exist in the system.",
        )
    
    # TODO: Send email with password reset link
    return {"msg": "Password recovery email sent"}

@router.post("/reset-password/", response_model=Msg)
async def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Reset password
    """
    # TODO: Implement password reset logic
    return {"msg": "Password updated successfully"}
