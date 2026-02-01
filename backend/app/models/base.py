"""
Base model mixins and utilities for SQLAlchemy models.

Provides common fields (id, timestamps) and utilities for all models.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TimestampMixin:
    """
    Mixin that adds created_at and updated_at timestamps to models.

    Timestamps are automatically managed by the database.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class BaseModel(TimestampMixin, Base):
    """
    Abstract base model with UUID primary key and timestamps.

    All application models should inherit from this class.
    Provides:
        - UUID primary key
        - created_at timestamp (auto-set on insert)
        - updated_at timestamp (auto-updated on changes)
    """

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    def __repr__(self) -> str:
        """Return string representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
