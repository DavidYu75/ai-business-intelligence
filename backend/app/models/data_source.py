"""
DataSource model for database connections.
"""

import uuid
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.query import Query


class DataSourceType(str, Enum):
    """Supported database types."""

    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    CSV = "csv"


class DataSource(BaseModel):
    """
    DataSource model for external database connections.

    Stores connection information for databases that users can query.
    Credentials are stored encrypted (encryption handled at service layer).
    """

    __tablename__ = "data_sources"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    type: Mapped[DataSourceType] = mapped_column(
        SQLEnum(DataSourceType),
        nullable=False,
    )

    # Connection details
    host: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    port: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    database: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    username: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    # Encrypted password - actual encryption at service layer
    encrypted_password: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # For file-based sources (CSV, SQLite)
    file_path: Mapped[Optional[str]] = mapped_column(
        String(1024),
        nullable=True,
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Schema cache (JSON stored as text)
    schema_cache: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Organization ownership
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="data_sources",
    )
    queries: Mapped[List["Query"]] = relationship(
        "Query",
        back_populates="data_source",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<DataSource(id={self.id}, name={self.name}, type={self.type})>"
