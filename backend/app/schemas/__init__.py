"""
Schemas package.

Exports all Pydantic schemas for API request/response validation.
"""

from app.schemas.dashboard import (
    DashboardBase,
    DashboardCreate,
    DashboardResponse,
    DashboardUpdate,
    DashboardWidgetBase,
    DashboardWidgetCreate,
    DashboardWidgetResponse,
    DashboardWidgetUpdate,
    DashboardWithWidgets,
)
from app.schemas.data_source import (
    DataSourceBase,
    DataSourceCreate,
    DataSourceResponse,
    DataSourceTestConnection,
    DataSourceTestResult,
    DataSourceUpdate,
)
from app.schemas.organization import (
    OrganizationBase,
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
    OrganizationWithMembers,
    UserOrganizationBase,
    UserOrganizationCreate,
    UserOrganizationResponse,
)
from app.schemas.query import (
    QueryBase,
    QueryCreate,
    QueryExecute,
    QueryExecuteResult,
    QueryHistory,
    QueryResponse,
    QueryUpdate,
)
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserInDB,
    UserResponse,
    UserUpdate,
)

__all__ = [
    # User
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserInDB",
    # Organization
    "OrganizationBase",
    "OrganizationCreate",
    "OrganizationUpdate",
    "OrganizationResponse",
    "OrganizationWithMembers",
    "UserOrganizationBase",
    "UserOrganizationCreate",
    "UserOrganizationResponse",
    # DataSource
    "DataSourceBase",
    "DataSourceCreate",
    "DataSourceUpdate",
    "DataSourceResponse",
    "DataSourceTestConnection",
    "DataSourceTestResult",
    # Query
    "QueryBase",
    "QueryCreate",
    "QueryExecute",
    "QueryUpdate",
    "QueryResponse",
    "QueryExecuteResult",
    "QueryHistory",
    # Dashboard
    "DashboardBase",
    "DashboardCreate",
    "DashboardUpdate",
    "DashboardResponse",
    "DashboardWithWidgets",
    "DashboardWidgetBase",
    "DashboardWidgetCreate",
    "DashboardWidgetUpdate",
    "DashboardWidgetResponse",
]
