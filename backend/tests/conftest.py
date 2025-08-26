"""
Pytest configuration and fixtures for backend tests.
"""

import asyncio
import pytest
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import get_db
from app.core.config import settings


# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )
    yield engine
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest.fixture
async def client(test_session) -> AsyncGenerator[TestClient, None]:
    """Create a test client with overridden dependencies."""

    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
        "is_active": True,
    }


@pytest.fixture
def test_organization_data():
    """Sample organization data for testing."""
    return {
        "name": "Test Organization",
        "description": "A test organization",
        "is_active": True,
    }


@pytest.fixture
def test_datasource_data():
    """Sample data source data for testing."""
    return {
        "name": "Test Database",
        "type": "postgresql",
        "host": "localhost",
        "port": 5432,
        "database": "test_db",
        "username": "test_user",
        "password": "test_password",
        "is_active": True,
    }


@pytest.fixture
def test_query_data():
    """Sample query data for testing."""
    return {
        "natural_language_query": "Show me all users",
        "generated_sql": "SELECT * FROM users",
        "data_source_id": 1,
        "is_active": True,
    }


@pytest.fixture
def test_dashboard_data():
    """Sample dashboard data for testing."""
    return {
        "name": "Test Dashboard",
        "description": "A test dashboard",
        "layout": {},
        "is_active": True,
    }
