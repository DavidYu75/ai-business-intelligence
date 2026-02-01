"""
Organization Pydantic schemas for request/response validation.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.organization import OrganizationRole


class OrganizationBase(BaseModel):
    """Base schema for Organization."""

    name: str = Field(..., min_length=1, max_length=255, description="Organization name")
    description: Optional[str] = Field(None, description="Organization description")


class OrganizationCreate(OrganizationBase):
    """Schema for creating a new organization."""

    pass


class OrganizationUpdate(BaseModel):
    """Schema for updating organization fields."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated name")
    description: Optional[str] = Field(None, description="Updated description")
    is_active: Optional[bool] = Field(None, description="Active status")


class OrganizationResponse(OrganizationBase):
    """Schema for organization response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Organization ID")
    is_active: bool = Field(..., description="Active status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class UserOrganizationBase(BaseModel):
    """Base schema for user-organization membership."""

    role: OrganizationRole = Field(
        OrganizationRole.MEMBER,
        description="User's role in the organization",
    )


class UserOrganizationCreate(UserOrganizationBase):
    """Schema for adding a user to an organization."""

    user_id: uuid.UUID = Field(..., description="User ID")
    organization_id: uuid.UUID = Field(..., description="Organization ID")


class UserOrganizationResponse(UserOrganizationBase):
    """Schema for user-organization membership response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Membership ID")
    user_id: uuid.UUID = Field(..., description="User ID")
    organization_id: uuid.UUID = Field(..., description="Organization ID")
    created_at: datetime = Field(..., description="Membership creation timestamp")


class OrganizationWithMembers(OrganizationResponse):
    """Organization response with member list."""

    members: List[UserOrganizationResponse] = Field(
        default_factory=list,
        description="Organization members",
    )
