"""User endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.api.deps import get_current_user, get_current_active_superuser
from api.db import get_db
from api.models import User as UserModel
from api.schemas import User as UserSchema, UserUpdate
from api.services.user import UserService

router = APIRouter()


@router.get("/users/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: UserModel = Depends(get_current_user),
):
    """Get current user information."""
    return current_user


@router.put("/users/me", response_model=UserSchema)
async def update_current_user(
    user_update: UserUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user information."""
    user_service = UserService(db)
    user = await user_service.update(current_user.id, user_update)
    return user


@router.get("/users/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_active_superuser),
):
    """Get user by ID (admin only)."""
    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return user
