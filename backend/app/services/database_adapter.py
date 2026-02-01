"""
Database adapter service for connecting to and querying external databases.

Provides a unified interface for PostgreSQL connections with schema introspection
and safe query execution.
"""

import asyncio
import json
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

import asyncpg
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.data_source import DataSource, DataSourceType


class DatabaseAdapter(ABC):
    """Abstract base class for database adapters."""

    @abstractmethod
    async def test_connection(self) -> Tuple[bool, str, Optional[float]]:
        """
        Test the database connection.

        Returns:
            Tuple of (success, message, latency_ms)
        """
        pass

    @abstractmethod
    async def get_schema(self) -> Dict[str, Any]:
        """
        Get the database schema (tables, columns, types).

        Returns:
            Schema dictionary with table and column information
        """
        pass

    @abstractmethod
    async def execute_query(
        self, query: str, timeout: float = 30.0
    ) -> Tuple[List[Dict[str, Any]], List[str], float]:
        """
        Execute a read-only SQL query.

        Args:
            query: SQL query string
            timeout: Query timeout in seconds

        Returns:
            Tuple of (rows, column_names, execution_time_ms)
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the database connection."""
        pass


class PostgreSQLAdapter(DatabaseAdapter):
    """PostgreSQL database adapter using asyncpg."""

    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        username: str,
        password: str,
    ):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self._pool: Optional[asyncpg.Pool] = None

    async def _get_pool(self) -> asyncpg.Pool:
        """Get or create connection pool."""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password,
                min_size=1,
                max_size=5,
                command_timeout=60,
            )
        return self._pool

    async def test_connection(self) -> Tuple[bool, str, Optional[float]]:
        """Test PostgreSQL connection."""
        start_time = time.time()
        try:
            pool = await asyncio.wait_for(self._get_pool(), timeout=10.0)
            async with pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            latency_ms = (time.time() - start_time) * 1000
            return True, "Connection successful", latency_ms
        except asyncio.TimeoutError:
            return False, "Connection timeout", None
        except asyncpg.InvalidCatalogNameError:
            return False, f"Database '{self.database}' does not exist", None
        except asyncpg.InvalidAuthorizationSpecificationError:
            return False, "Invalid username or password", None
        except asyncpg.PostgresConnectionError as e:
            return False, f"Connection failed: {str(e)}", None
        except Exception as e:
            return False, f"Unexpected error: {str(e)}", None

    async def get_schema(self) -> Dict[str, Any]:
        """
        Get PostgreSQL schema information.

        Returns schema with tables, columns, types, and relationships.
        """
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            # Get tables
            tables_query = """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """
            tables = await conn.fetch(tables_query)

            schema = {"tables": {}}

            for table_row in tables:
                table_name = table_row["table_name"]

                # Get columns for this table
                columns_query = """
                    SELECT 
                        column_name,
                        data_type,
                        is_nullable,
                        column_default,
                        character_maximum_length
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                    AND table_name = $1
                    ORDER BY ordinal_position
                """
                columns = await conn.fetch(columns_query, table_name)

                # Get primary keys
                pk_query = """
                    SELECT a.attname as column_name
                    FROM pg_index i
                    JOIN pg_attribute a ON a.attrelid = i.indrelid
                        AND a.attnum = ANY(i.indkey)
                    WHERE i.indrelid = $1::regclass
                    AND i.indisprimary
                """
                try:
                    pks = await conn.fetch(pk_query, table_name)
                    primary_keys = [pk["column_name"] for pk in pks]
                except Exception:
                    primary_keys = []

                schema["tables"][table_name] = {
                    "columns": [
                        {
                            "name": col["column_name"],
                            "type": col["data_type"],
                            "nullable": col["is_nullable"] == "YES",
                            "default": col["column_default"],
                            "max_length": col["character_maximum_length"],
                        }
                        for col in columns
                    ],
                    "primary_keys": primary_keys,
                }

            # Get row counts for each table
            for table_name in schema["tables"]:
                try:
                    count = await conn.fetchval(
                        f'SELECT COUNT(*) FROM "{table_name}"'
                    )
                    schema["tables"][table_name]["row_count"] = count
                except Exception:
                    schema["tables"][table_name]["row_count"] = None

            return schema

    async def execute_query(
        self, query: str, timeout: float = 30.0
    ) -> Tuple[List[Dict[str, Any]], List[str], float]:
        """
        Execute a read-only SQL query.

        Args:
            query: SQL query (must be SELECT)
            timeout: Query timeout in seconds

        Returns:
            Tuple of (rows as dicts, column names, execution time ms)

        Raises:
            ValueError: If query is not a SELECT statement
            asyncpg.PostgresError: On database errors
        """
        # Validate query is read-only
        normalized = query.strip().upper()
        if not normalized.startswith("SELECT") and not normalized.startswith("WITH"):
            raise ValueError("Only SELECT queries are allowed")

        # Block dangerous operations
        dangerous_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "TRUNCATE", "ALTER", "CREATE"]
        for keyword in dangerous_keywords:
            if keyword in normalized:
                raise ValueError(f"Query contains forbidden keyword: {keyword}")

        pool = await self._get_pool()
        start_time = time.time()

        async with pool.acquire() as conn:
            try:
                rows = await asyncio.wait_for(
                    conn.fetch(query),
                    timeout=timeout
                )
                execution_time_ms = (time.time() - start_time) * 1000

                # Convert to list of dicts
                if rows:
                    column_names = list(rows[0].keys())
                    result = [dict(row) for row in rows]
                else:
                    column_names = []
                    result = []

                return result, column_names, execution_time_ms

            except asyncio.TimeoutError:
                raise ValueError(f"Query timeout after {timeout} seconds")

    async def close(self) -> None:
        """Close the connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None


class DataSourceService:
    """Service for managing data sources and their connections."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._adapters: Dict[UUID, DatabaseAdapter] = {}

    async def get_data_source(self, data_source_id: UUID) -> Optional[DataSource]:
        """Get a data source by ID."""
        result = await self.db.execute(
            select(DataSource).where(DataSource.id == data_source_id)
        )
        return result.scalar_one_or_none()

    async def get_data_sources_by_org(self, organization_id: UUID) -> List[DataSource]:
        """Get all data sources for an organization."""
        result = await self.db.execute(
            select(DataSource)
            .where(DataSource.organization_id == organization_id)
            .where(DataSource.is_active == True)
            .order_by(DataSource.name)
        )
        return list(result.scalars().all())

    async def create_data_source(
        self,
        name: str,
        type: DataSourceType,
        organization_id: UUID,
        description: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        file_path: Optional[str] = None,
    ) -> DataSource:
        """Create a new data source."""
        data_source = DataSource(
            name=name,
            type=type,
            description=description,
            organization_id=organization_id,
            host=host,
            port=port,
            database=database,
            username=username,
            encrypted_password=password,  # TODO: Encrypt in production
            file_path=file_path,
        )
        self.db.add(data_source)
        await self.db.flush()
        await self.db.refresh(data_source)
        return data_source

    async def update_data_source(
        self,
        data_source: DataSource,
        **kwargs,
    ) -> DataSource:
        """Update a data source."""
        for field, value in kwargs.items():
            if value is not None:
                if field == "password":
                    setattr(data_source, "encrypted_password", value)  # TODO: Encrypt
                else:
                    setattr(data_source, field, value)
        await self.db.flush()
        await self.db.refresh(data_source)
        return data_source

    async def delete_data_source(self, data_source: DataSource) -> None:
        """Delete a data source."""
        await self.db.delete(data_source)
        await self.db.flush()

    def _create_adapter(self, data_source: DataSource, password: Optional[str] = None) -> DatabaseAdapter:
        """Create an adapter for the data source type."""
        if data_source.type == DataSourceType.POSTGRESQL:
            return PostgreSQLAdapter(
                host=data_source.host or "localhost",
                port=data_source.port or 5432,
                database=data_source.database or "",
                username=data_source.username or "",
                password=password or data_source.encrypted_password or "",
            )
        else:
            raise ValueError(f"Unsupported data source type: {data_source.type}")

    async def test_connection(
        self,
        data_source: Optional[DataSource] = None,
        *,
        type: Optional[DataSourceType] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> Tuple[bool, str, Optional[float]]:
        """
        Test a data source connection.

        Can test either an existing data source or new connection parameters.
        """
        if data_source:
            adapter = self._create_adapter(data_source, password)
        elif type == DataSourceType.POSTGRESQL:
            adapter = PostgreSQLAdapter(
                host=host or "localhost",
                port=port or 5432,
                database=database or "",
                username=username or "",
                password=password or "",
            )
        else:
            return False, f"Unsupported type: {type}", None

        try:
            return await adapter.test_connection()
        finally:
            await adapter.close()

    async def get_schema(self, data_source: DataSource) -> Dict[str, Any]:
        """Get schema for a data source."""
        # Check cache first
        if data_source.schema_cache:
            try:
                return json.loads(data_source.schema_cache)
            except json.JSONDecodeError:
                pass

        adapter = self._create_adapter(data_source)
        try:
            schema = await adapter.get_schema()
            # Cache the schema
            data_source.schema_cache = json.dumps(schema)
            await self.db.flush()
            return schema
        finally:
            await adapter.close()

    async def execute_query(
        self,
        data_source: DataSource,
        query: str,
        timeout: float = 30.0,
    ) -> Tuple[List[Dict[str, Any]], List[str], float]:
        """Execute a query on a data source."""
        adapter = self._create_adapter(data_source)
        try:
            return await adapter.execute_query(query, timeout)
        finally:
            await adapter.close()
