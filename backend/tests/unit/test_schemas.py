"""
Tests for Pydantic schemas.
"""

import uuid
from datetime import datetime

import pytest
from pydantic import ValidationError


class TestUserSchemas:
    """Test cases for User schemas."""

    def test_user_create_valid(self):
        """Test UserCreate with valid data."""
        from app.schemas.user import UserCreate

        user = UserCreate(
            email="test@example.com",
            password="securepassword123",
            full_name="Test User",
        )
        assert user.email == "test@example.com"
        assert user.password == "securepassword123"

    def test_user_create_invalid_email(self):
        """Test UserCreate rejects invalid email."""
        from app.schemas.user import UserCreate

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="not-an-email", password="securepassword123")
        assert "email" in str(exc_info.value).lower()

    def test_user_create_password_too_short(self):
        """Test UserCreate enforces minimum password length."""
        from app.schemas.user import UserCreate

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="test@example.com", password="short")
        assert "password" in str(exc_info.value).lower()

    def test_user_response_from_attributes(self):
        """Test UserResponse can be created from model attributes."""
        from app.schemas.user import UserResponse

        user = UserResponse(
            id=uuid.uuid4(),
            email="test@example.com",
            full_name="Test User",
            is_active=True,
            is_superuser=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert user.email == "test@example.com"
        assert user.is_active is True


class TestOrganizationSchemas:
    """Test cases for Organization schemas."""

    def test_organization_create_valid(self):
        """Test OrganizationCreate with valid data."""
        from app.schemas.organization import OrganizationCreate

        org = OrganizationCreate(name="Test Org", description="A test organization")
        assert org.name == "Test Org"

    def test_organization_create_name_required(self):
        """Test OrganizationCreate requires name."""
        from app.schemas.organization import OrganizationCreate

        with pytest.raises(ValidationError):
            OrganizationCreate(description="Missing name")

    def test_user_organization_create(self):
        """Test UserOrganizationCreate with role."""
        from app.models.organization import OrganizationRole
        from app.schemas.organization import UserOrganizationCreate

        membership = UserOrganizationCreate(
            user_id=uuid.uuid4(),
            organization_id=uuid.uuid4(),
            role=OrganizationRole.ADMIN,
        )
        assert membership.role == OrganizationRole.ADMIN


class TestDataSourceSchemas:
    """Test cases for DataSource schemas."""

    def test_datasource_create_valid(self):
        """Test DataSourceCreate with valid data."""
        from app.models.data_source import DataSourceType
        from app.schemas.data_source import DataSourceCreate

        ds = DataSourceCreate(
            name="Test DB",
            type=DataSourceType.POSTGRESQL,
            host="localhost",
            port=5432,
            database="testdb",
            username="user",
            password="pass",
            organization_id=uuid.uuid4(),
        )
        assert ds.name == "Test DB"
        assert ds.type == DataSourceType.POSTGRESQL
        assert ds.port == 5432

    def test_datasource_create_invalid_port(self):
        """Test DataSourceCreate rejects invalid port."""
        from app.models.data_source import DataSourceType
        from app.schemas.data_source import DataSourceCreate

        with pytest.raises(ValidationError):
            DataSourceCreate(
                name="Test DB",
                type=DataSourceType.POSTGRESQL,
                port=99999,  # Invalid port
                organization_id=uuid.uuid4(),
            )


class TestQuerySchemas:
    """Test cases for Query schemas."""

    def test_query_create_valid(self):
        """Test QueryCreate with valid data."""
        from app.schemas.query import QueryCreate

        query = QueryCreate(
            natural_language_query="Show me all users",
            data_source_id=uuid.uuid4(),
            name="All Users Query",
        )
        assert query.natural_language_query == "Show me all users"

    def test_query_create_empty_query_rejected(self):
        """Test QueryCreate rejects empty query."""
        from app.schemas.query import QueryCreate

        with pytest.raises(ValidationError):
            QueryCreate(natural_language_query="", data_source_id=uuid.uuid4())

    def test_query_execute_result(self):
        """Test QueryExecuteResult schema."""
        from app.schemas.query import QueryExecuteResult

        result = QueryExecuteResult(
            natural_language_query="Show users",
            generated_sql="SELECT * FROM users",
            execution_time_ms=42.5,
            columns=["id", "name", "email"],
            rows=[{"id": 1, "name": "Test", "email": "test@example.com"}],
            row_count=1,
        )
        assert result.row_count == 1
        assert len(result.columns) == 3


class TestDashboardSchemas:
    """Test cases for Dashboard schemas."""

    def test_dashboard_create_valid(self):
        """Test DashboardCreate with valid data."""
        from app.schemas.dashboard import DashboardCreate

        dashboard = DashboardCreate(
            name="Sales Dashboard",
            description="Monthly sales overview",
            organization_id=uuid.uuid4(),
        )
        assert dashboard.name == "Sales Dashboard"
        assert dashboard.is_public is False

    def test_dashboard_widget_create(self):
        """Test DashboardWidgetCreate with positioning."""
        from app.schemas.dashboard import DashboardWidgetCreate

        widget = DashboardWidgetCreate(
            name="Revenue Chart",
            widget_type="bar_chart",
            position_x=0,
            position_y=0,
            width=6,
            height=4,
        )
        assert widget.widget_type == "bar_chart"
        assert widget.width == 6

    def test_dashboard_widget_invalid_width(self):
        """Test DashboardWidgetCreate rejects invalid width."""
        from app.schemas.dashboard import DashboardWidgetCreate

        with pytest.raises(ValidationError):
            DashboardWidgetCreate(
                widget_type="chart",
                width=15,  # Max is 12
            )
