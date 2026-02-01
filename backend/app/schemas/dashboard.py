"""
Dashboard Pydantic schemas for request/response validation.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class DashboardWidgetBase(BaseModel):
    """Base schema for DashboardWidget."""

    name: Optional[str] = Field(None, max_length=255, description="Widget name")
    widget_type: str = Field(..., max_length=50, description="Widget type (chart, table, etc)")
    config: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Widget configuration",
    )
    position_x: int = Field(0, ge=0, description="X position in grid")
    position_y: int = Field(0, ge=0, description="Y position in grid")
    width: int = Field(4, ge=1, le=12, description="Width in grid units")
    height: int = Field(3, ge=1, le=12, description="Height in grid units")


class DashboardWidgetCreate(DashboardWidgetBase):
    """Schema for creating a new widget."""

    query_id: Optional[uuid.UUID] = Field(None, description="Associated query ID")


class DashboardWidgetUpdate(BaseModel):
    """Schema for updating widget fields."""

    name: Optional[str] = Field(None, max_length=255, description="Updated name")
    widget_type: Optional[str] = Field(None, max_length=50, description="Updated type")
    config: Optional[Dict[str, Any]] = Field(None, description="Updated configuration")
    position_x: Optional[int] = Field(None, ge=0, description="Updated X position")
    position_y: Optional[int] = Field(None, ge=0, description="Updated Y position")
    width: Optional[int] = Field(None, ge=1, le=12, description="Updated width")
    height: Optional[int] = Field(None, ge=1, le=12, description="Updated height")
    query_id: Optional[uuid.UUID] = Field(None, description="Updated query ID")


class DashboardWidgetResponse(DashboardWidgetBase):
    """Schema for widget response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Widget ID")
    query_id: Optional[uuid.UUID] = Field(None, description="Associated query ID")
    dashboard_id: uuid.UUID = Field(..., description="Parent dashboard ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class DashboardBase(BaseModel):
    """Base schema for Dashboard."""

    name: str = Field(..., min_length=1, max_length=255, description="Dashboard name")
    description: Optional[str] = Field(None, description="Dashboard description")


class DashboardCreate(DashboardBase):
    """Schema for creating a new dashboard."""

    organization_id: uuid.UUID = Field(..., description="Organization ID")
    layout: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Layout configuration",
    )
    is_public: bool = Field(False, description="Public visibility")
    widgets: List[DashboardWidgetCreate] = Field(
        default_factory=list,
        description="Initial widgets",
    )


class DashboardUpdate(BaseModel):
    """Schema for updating dashboard fields."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated name")
    description: Optional[str] = Field(None, description="Updated description")
    layout: Optional[Dict[str, Any]] = Field(None, description="Updated layout")
    is_public: Optional[bool] = Field(None, description="Updated visibility")
    is_active: Optional[bool] = Field(None, description="Active status")


class DashboardResponse(DashboardBase):
    """Schema for dashboard response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Dashboard ID")
    layout: Optional[Dict[str, Any]] = Field(None, description="Layout configuration")
    is_public: bool = Field(..., description="Public visibility")
    is_active: bool = Field(..., description="Active status")
    owner_id: uuid.UUID = Field(..., description="Owner user ID")
    organization_id: uuid.UUID = Field(..., description="Organization ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class DashboardWithWidgets(DashboardResponse):
    """Dashboard response with widgets."""

    widgets: List[DashboardWidgetResponse] = Field(
        default_factory=list,
        description="Dashboard widgets",
    )
