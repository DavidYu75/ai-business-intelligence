"""
Dashboard model for storing user dashboards and widgets.
"""

import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User


class Dashboard(BaseModel):
    """
    Dashboard model for storing user-created dashboards.

    Dashboards contain multiple widgets arranged in a layout.
    """

    __tablename__ = "dashboards"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Layout configuration (JSON)
    layout: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        default=dict,
    )

    # Sharing settings
    is_public: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Ownership
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Relationships
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="dashboards",
    )
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="dashboards",
    )
    widgets: Mapped[List["DashboardWidget"]] = relationship(
        "DashboardWidget",
        back_populates="dashboard",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Dashboard(id={self.id}, name={self.name})>"


class DashboardWidget(BaseModel):
    """
    Widget model for individual dashboard components.

    Each widget displays a visualization of query results.
    """

    __tablename__ = "dashboard_widgets"

    name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    widget_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Widget configuration (JSON)
    config: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        default=dict,
    )

    # Position in dashboard grid
    position_x: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    position_y: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    width: Mapped[int] = mapped_column(
        Integer,
        default=4,
        nullable=False,
    )
    height: Mapped[int] = mapped_column(
        Integer,
        default=3,
        nullable=False,
    )

    # Associated query (optional - widgets can have static content)
    query_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("queries.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Parent dashboard
    dashboard_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dashboards.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Relationships
    dashboard: Mapped["Dashboard"] = relationship(
        "Dashboard",
        back_populates="widgets",
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<DashboardWidget(id={self.id}, type={self.widget_type})>"
