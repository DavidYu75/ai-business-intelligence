"""
Authentication API endpoints for user registration, login, and token management.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import CurrentUser, DbSession
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ==================== Schemas ====================


class Token(BaseModel):
    """Response schema for authentication tokens."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenRefresh(BaseModel):
    """Request schema for token refresh."""

    refresh_token: str = Field(..., description="Refresh token to exchange")


class LoginRequest(BaseModel):
    """Request schema for login."""

    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")


# ==================== Endpoints ====================


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
)
async def register(
    user_in: UserCreate,
    db: DbSession,
) -> UserResponse:
    """
    Register a new user account.

    - **email**: Unique email address
    - **password**: Password (min 8 characters)
    - **full_name**: Optional full name
    """
    auth_service = AuthService(db)

    # Check if email already exists
    existing_user = await auth_service.get_user_by_email(user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    user = await auth_service.create_user(user_in)
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=Token,
    summary="Login and get tokens",
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
) -> Token:
    """
    Authenticate user and return access/refresh tokens.

    Uses OAuth2 password flow - send credentials as form data:
    - **username**: User email (OAuth2 spec uses 'username')
    - **password**: User password
    """
    auth_service = AuthService(db)

    # Authenticate user (OAuth2 form uses 'username' for email)
    user = await auth_service.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Generate tokens
    access_token = AuthService.create_access_token(subject=user.id)
    refresh_token = AuthService.create_refresh_token(subject=user.id)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post(
    "/login/json",
    response_model=Token,
    summary="Login with JSON body",
)
async def login_json(
    login_data: LoginRequest,
    db: DbSession,
) -> Token:
    """
    Authenticate user with JSON body (alternative to form-based login).

    - **email**: User email
    - **password**: User password
    """
    auth_service = AuthService(db)

    user = await auth_service.authenticate(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    access_token = AuthService.create_access_token(subject=user.id)
    refresh_token = AuthService.create_refresh_token(subject=user.id)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh access token",
)
async def refresh_token(
    token_data: TokenRefresh,
    db: DbSession,
) -> Token:
    """
    Exchange a refresh token for new access/refresh tokens.

    - **refresh_token**: Valid refresh token
    """
    # Decode refresh token
    payload = AuthService.decode_token(token_data.refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Verify it's a refresh token
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    # Get user
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Generate new tokens
    access_token = AuthService.create_access_token(subject=user.id)
    refresh_token = AuthService.create_refresh_token(subject=user.id)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
)
async def get_current_user_info(
    current_user: CurrentUser,
) -> UserResponse:
    """
    Get the currently authenticated user's information.

    Requires valid access token in Authorization header.
    """
    return UserResponse.model_validate(current_user)
