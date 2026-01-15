"""Authentication endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from sqlalchemy.ext.asyncio import AsyncSession

from api.core import verify_password, create_access_token
from api.db import get_db
from api.schemas import Token, UserCreate, User as UserSchema
from api.services.user import UserService

router = APIRouter()
basic_auth = HTTPBasic()


@router.post("/auth/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user."""
    user_service = UserService(db)
    
    # Check if user exists
    existing_user = await user_service.get_by_email(user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    existing_user = await user_service.get_by_username(user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    
    # Create user
    user = await user_service.create(user_in)
    return user


@router.post("/auth/login", response_model=Token)
async def login(
    credentials: HTTPBasicCredentials = Depends(basic_auth),
    db: AsyncSession = Depends(get_db),
):
    """Login and get access token."""
    user_service = UserService(db)
    user = await user_service.get_by_username(credentials.username)
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token)
