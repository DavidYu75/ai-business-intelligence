"""
Query model for storing user queries and results.
"""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.data_source import DataSource
    from app.models.user import User


class Query(BaseModel):
    """
    Query model for storing natural language queries and their SQL translations.

    Tracks query history, execution metrics, and favorites.
    """

    __tablename__ = "queries"

    # Query content
    natural_language_query: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    generated_sql: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Execution metadata
    execution_time_ms: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    result_rows_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # User preferences
    is_favorite: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    # Relationships
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    data_source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("data_sources.id", ondelete="CASCADE"),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="queries",
    )
    data_source: Mapped["DataSource"] = relationship(
        "DataSource",
        back_populates="queries",
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Query(id={self.id}, user_id={self.user_id})>"
