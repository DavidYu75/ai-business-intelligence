"""
Tests for core configuration module.
"""

import os
from unittest.mock import patch

import pytest


class TestSettings:
    """Test cases for application settings."""

    def test_settings_loads_defaults(self):
        """Test that settings load with default values."""
        from app.core.config import Settings

        settings = Settings(
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
            SECRET_KEY="test-secret-key",
            _env_file=None,  # Disable .env file loading
        )
        assert settings.PROJECT_NAME == "Real-Time BI Platform"
        assert settings.API_V1_STR == "/api/v1"
        assert settings.ALGORITHM == "HS256"
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30

    def test_settings_database_url_required(self):
        """Test that DATABASE_URL is required when not in environment."""
        from pydantic import ValidationError

        from app.core.config import Settings

        # Clear env vars and disable .env file to test required field
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings(
                    SECRET_KEY="test-secret-key",
                    _env_file=None,
                )
            assert "DATABASE_URL" in str(exc_info.value)

    def test_settings_secret_key_required(self):
        """Test that SECRET_KEY is required when not in environment."""
        from pydantic import ValidationError

        from app.core.config import Settings

        # Clear env vars and disable .env file to test required field
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings(
                    DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
                    _env_file=None,
                )
            assert "SECRET_KEY" in str(exc_info.value)

    def test_settings_cors_origins_parsing(self):
        """Test CORS origins are parsed correctly."""
        from app.core.config import Settings

        settings = Settings(
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
            SECRET_KEY="test-secret-key",
            BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"],
            _env_file=None,
        )
        assert len(settings.BACKEND_CORS_ORIGINS) == 2
        assert "http://localhost:3000" in settings.BACKEND_CORS_ORIGINS

    def test_settings_cors_origins_from_json_string(self):
        """Test CORS origins parsed from JSON string (common in env vars)."""
        from app.core.config import Settings

        settings = Settings(
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
            SECRET_KEY="test-secret-key",
            BACKEND_CORS_ORIGINS='["http://localhost:3000", "http://example.com"]',
            _env_file=None,
        )
        assert len(settings.BACKEND_CORS_ORIGINS) == 2
        assert "http://example.com" in settings.BACKEND_CORS_ORIGINS

    def test_settings_cors_origins_from_comma_separated(self):
        """Test CORS origins parsed from comma-separated string."""
        from app.core.config import Settings

        settings = Settings(
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
            SECRET_KEY="test-secret-key",
            BACKEND_CORS_ORIGINS="http://localhost:3000, http://example.com",
            _env_file=None,
        )
        assert len(settings.BACKEND_CORS_ORIGINS) == 2
        assert "http://example.com" in settings.BACKEND_CORS_ORIGINS

    def test_settings_redis_url_default(self):
        """Test Redis URL has sensible default."""
        from app.core.config import Settings

        settings = Settings(
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
            SECRET_KEY="test-secret-key",
            _env_file=None,
        )
        assert settings.REDIS_URL == "redis://localhost:6379"

    def test_settings_pool_settings(self):
        """Test database pool settings."""
        from app.core.config import Settings

        settings = Settings(
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
            SECRET_KEY="test-secret-key",
            DB_POOL_SIZE=10,
            DB_MAX_OVERFLOW=20,
            _env_file=None,
        )
        assert settings.DB_POOL_SIZE == 10
        assert settings.DB_MAX_OVERFLOW == 20

    def test_settings_secret_key_min_length(self):
        """Test SECRET_KEY enforces minimum length."""
        from pydantic import ValidationError

        from app.core.config import Settings

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings(
                    DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
                    SECRET_KEY="short",  # Too short
                    _env_file=None,
                )
            assert "SECRET_KEY" in str(exc_info.value)
