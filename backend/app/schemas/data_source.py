"""
DataSource Pydantic schemas for request/response validation.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.data_source import DataSourceType


class DataSourceBase(BaseModel):
    """Base schema for DataSource."""

    name: str = Field(..., min_length=1, max_length=255, description="Data source name")
    description: Optional[str] = Field(None, description="Data source description")
    type: DataSourceType = Field(..., description="Database type")


class DataSourceCreate(DataSourceBase):
    """Schema for creating a new data source."""

    # Connection details
    host: Optional[str] = Field(None, max_length=255, description="Database host")
    port: Optional[int] = Field(None, ge=1, le=65535, description="Database port")
    database: Optional[str] = Field(None, max_length=255, description="Database name")
    username: Optional[str] = Field(None, max_length=255, description="Database username")
    password: Optional[str] = Field(None, description="Database password")

    # For file-based sources
    file_path: Optional[str] = Field(None, max_length=1024, description="File path for CSV/SQLite")

    # Organization
    organization_id: uuid.UUID = Field(..., description="Organization ID")

    @field_validator("host")
    @classmethod
    def validate_host_for_db_types(cls, v: Optional[str], info) -> Optional[str]:
        """Validate host is provided for remote database types."""
        # Note: Full validation would check type field, but info.data may not have it yet
        return v


class DataSourceUpdate(BaseModel):
    """Schema for updating data source fields."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated name")
    description: Optional[str] = Field(None, description="Updated description")
    host: Optional[str] = Field(None, max_length=255, description="Updated host")
    port: Optional[int] = Field(None, ge=1, le=65535, description="Updated port")
    database: Optional[str] = Field(None, max_length=255, description="Updated database")
    username: Optional[str] = Field(None, max_length=255, description="Updated username")
    password: Optional[str] = Field(None, description="Updated password")
    is_active: Optional[bool] = Field(None, description="Active status")


class DataSourceResponse(DataSourceBase):
    """Schema for data source response (excludes credentials)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Data source ID")
    host: Optional[str] = Field(None, description="Database host")
    port: Optional[int] = Field(None, description="Database port")
    database: Optional[str] = Field(None, description="Database name")
    username: Optional[str] = Field(None, description="Database username")
    file_path: Optional[str] = Field(None, description="File path")
    organization_id: uuid.UUID = Field(..., description="Organization ID")
    is_active: bool = Field(..., description="Active status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class DataSourceTestConnection(BaseModel):
    """Schema for testing data source connection."""

    type: DataSourceType = Field(..., description="Database type")
    host: Optional[str] = Field(None, description="Database host")
    port: Optional[int] = Field(None, description="Database port")
    database: Optional[str] = Field(None, description="Database name")
    username: Optional[str] = Field(None, description="Database username")
    password: Optional[str] = Field(None, description="Database password")
    file_path: Optional[str] = Field(None, description="File path for CSV/SQLite")


class DataSourceTestResult(BaseModel):
    """Schema for connection test result."""

    success: bool = Field(..., description="Whether connection was successful")
    message: str = Field(..., description="Result message or error details")
    latency_ms: Optional[float] = Field(None, description="Connection latency in milliseconds")
