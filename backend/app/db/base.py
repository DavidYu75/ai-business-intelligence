"""
SQLAlchemy base configuration.

Provides the DeclarativeBase for all models and shared metadata.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.

    All models should inherit from this class to be included in
    metadata and migrations.
    """

    pass
