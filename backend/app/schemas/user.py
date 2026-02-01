"""
User Pydantic schemas for request/response validation.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base schema for User with common fields."""

    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, max_length=255, description="User's full name")


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User password (min 8 characters)",
    )


class UserUpdate(BaseModel):
    """Schema for updating user fields."""

    email: Optional[EmailStr] = Field(None, description="Updated email address")
    full_name: Optional[str] = Field(None, max_length=255, description="Updated full name")
    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=128,
        description="New password (min 8 characters)",
    )
    is_active: Optional[bool] = Field(None, description="Account active status")


class UserResponse(UserBase):
    """Schema for user response (excludes sensitive data)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="User ID")
    is_active: bool = Field(..., description="Account active status")
    is_superuser: bool = Field(..., description="Superuser status")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class UserInDB(UserResponse):
    """Schema for user with hashed password (internal use only)."""

    hashed_password: str = Field(..., description="Hashed password")
