"""
Tests for SQLAlchemy models.
"""

import uuid
from datetime import datetime

import pytest


class TestBaseModel:
    """Test cases for BaseModel."""

    def test_base_model_has_uuid_id(self):
        """Test that BaseModel generates UUID primary keys."""
        from app.models.base import BaseModel

        # BaseModel is abstract, so we check the mapped column definition
        assert hasattr(BaseModel, "id")
        assert BaseModel.__abstract__ is True

    def test_timestamp_mixin_fields(self):
        """Test that TimestampMixin provides timestamp fields."""
        from app.models.base import TimestampMixin

        assert hasattr(TimestampMixin, "created_at")
        assert hasattr(TimestampMixin, "updated_at")


class TestUserModel:
    """Test cases for User model."""

    def test_user_has_required_fields(self):
        """Test User model has all required fields."""
        from app.models.user import User

        # Check table name
        assert User.__tablename__ == "users"

        # Check required fields exist
        columns = {c.name for c in User.__table__.columns}
        assert "id" in columns
        assert "email" in columns
        assert "hashed_password" in columns
        assert "full_name" in columns
        assert "is_active" in columns
        assert "is_superuser" in columns
        assert "created_at" in columns
        assert "updated_at" in columns

    def test_user_email_is_unique(self):
        """Test email column has unique constraint."""
        from app.models.user import User

        email_col = User.__table__.columns["email"]
        assert email_col.unique is True

    def test_user_email_is_indexed(self):
        """Test email column is indexed for fast lookups."""
        from app.models.user import User

        email_col = User.__table__.columns["email"]
        assert email_col.index is True


class TestOrganizationModel:
    """Test cases for Organization model."""

    def test_organization_has_required_fields(self):
        """Test Organization model has required fields."""
        from app.models.organization import Organization

        assert Organization.__tablename__ == "organizations"

        columns = {c.name for c in Organization.__table__.columns}
        assert "id" in columns
        assert "name" in columns
        assert "description" in columns
        assert "is_active" in columns

    def test_organization_role_enum(self):
        """Test OrganizationRole enum values."""
        from app.models.organization import OrganizationRole

        assert OrganizationRole.OWNER == "owner"
        assert OrganizationRole.ADMIN == "admin"
        assert OrganizationRole.MEMBER == "member"
        assert OrganizationRole.VIEWER == "viewer"


class TestUserOrganizationModel:
    """Test cases for UserOrganization junction table."""

    def test_user_organization_has_foreign_keys(self):
        """Test UserOrganization has proper foreign keys."""
        from app.models.organization import UserOrganization

        assert UserOrganization.__tablename__ == "user_organizations"

        columns = {c.name for c in UserOrganization.__table__.columns}
        assert "user_id" in columns
        assert "organization_id" in columns
        assert "role" in columns


class TestDataSourceModel:
    """Test cases for DataSource model."""

    def test_datasource_has_required_fields(self):
        """Test DataSource model has required fields."""
        from app.models.data_source import DataSource

        assert DataSource.__tablename__ == "data_sources"

        columns = {c.name for c in DataSource.__table__.columns}
        assert "id" in columns
        assert "name" in columns
        assert "type" in columns
        assert "host" in columns
        assert "port" in columns
        assert "database" in columns
        assert "organization_id" in columns
        assert "is_active" in columns

    def test_datasource_type_enum(self):
        """Test DataSourceType enum values."""
        from app.models.data_source import DataSourceType

        assert DataSourceType.POSTGRESQL == "postgresql"
        assert DataSourceType.MYSQL == "mysql"
        assert DataSourceType.SQLITE == "sqlite"
        assert DataSourceType.CSV == "csv"


class TestQueryModel:
    """Test cases for Query model."""

    def test_query_has_required_fields(self):
        """Test Query model has required fields."""
        from app.models.query import Query

        assert Query.__tablename__ == "queries"

        columns = {c.name for c in Query.__table__.columns}
        assert "id" in columns
        assert "natural_language_query" in columns
        assert "generated_sql" in columns
        assert "user_id" in columns
        assert "data_source_id" in columns
        assert "execution_time_ms" in columns
        assert "is_favorite" in columns


class TestDashboardModel:
    """Test cases for Dashboard model."""

    def test_dashboard_has_required_fields(self):
        """Test Dashboard model has required fields."""
        from app.models.dashboard import Dashboard

        assert Dashboard.__tablename__ == "dashboards"

        columns = {c.name for c in Dashboard.__table__.columns}
        assert "id" in columns
        assert "name" in columns
        assert "description" in columns
        assert "layout" in columns
        assert "owner_id" in columns
        assert "organization_id" in columns
        assert "is_public" in columns
        assert "is_active" in columns

    def test_dashboard_widget_has_required_fields(self):
        """Test DashboardWidget model has required fields."""
        from app.models.dashboard import DashboardWidget

        assert DashboardWidget.__tablename__ == "dashboard_widgets"

        columns = {c.name for c in DashboardWidget.__table__.columns}
        assert "id" in columns
        assert "widget_type" in columns
        assert "config" in columns
        assert "position_x" in columns
        assert "position_y" in columns
        assert "width" in columns
        assert "height" in columns
        assert "dashboard_id" in columns
