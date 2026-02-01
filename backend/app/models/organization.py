"""
Organization model for multi-tenancy support.
"""

import uuid
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Enum as SQLEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.dashboard import Dashboard
    from app.models.data_source import DataSource
    from app.models.user import User


class OrganizationRole(str, Enum):
    """Roles a user can have within an organization."""

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class Organization(BaseModel):
    """
    Organization model for multi-tenancy.

    Organizations group users and resources together.
    """

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Relationships
    members: Mapped[List["UserOrganization"]] = relationship(
        "UserOrganization",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    data_sources: Mapped[List["DataSource"]] = relationship(
        "DataSource",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    dashboards: Mapped[List["Dashboard"]] = relationship(
        "Dashboard",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Organization(id={self.id}, name={self.name})>"


class UserOrganization(BaseModel):
    """
    Junction table for User-Organization many-to-many relationship.

    Includes the user's role within the organization.
    """

    __tablename__ = "user_organizations"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[OrganizationRole] = mapped_column(
        SQLEnum(OrganizationRole),
        default=OrganizationRole.MEMBER,
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="organizations",
    )
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="members",
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<UserOrganization(user_id={self.user_id}, org_id={self.organization_id}, role={self.role})>"
