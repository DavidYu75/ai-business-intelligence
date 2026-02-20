"""
Query executor service for orchestrating NL→SQL→Results pipeline.

Coordinates between NLP service, database adapter, and query storage.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.data_source import DataSource
from app.models.query import Query
from app.services.database_adapter import DataSourceService
from app.services.nlp_service import NLPService


class QueryExecutor:
    """
    Orchestrates the full query pipeline:
    1. Fetch data source and schema
    2. Generate SQL from natural language via Claude
    3. Execute SQL against the target database
    4. Store results in query history
    """

    # Max rows returned in API response (prevent memory issues)
    MAX_RESPONSE_ROWS = 500

    def __init__(self, db: AsyncSession):
        self.db = db
        self.data_source_service = DataSourceService(db)
        self.nlp_service = NLPService()

    async def execute_nl_query(
        self,
        natural_language_query: str,
        data_source_id: UUID,
        user_id: UUID,
        save: bool = True,
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute a natural language query end-to-end.

        Args:
            natural_language_query: User's plain English question
            data_source_id: Target data source to query
            user_id: ID of the requesting user
            save: Whether to save to query history
            name: Optional name for the query

        Returns:
            Dict with generated SQL, columns, rows, timing, etc.

        Raises:
            ValueError: If data source not found or query fails
        """
        # 1. Get the data source
        data_source = await self.data_source_service.get_data_source(data_source_id)
        if not data_source:
            raise ValueError("Data source not found")

        if not data_source.is_active:
            raise ValueError("Data source is inactive")

        # 2. Get schema for context
        try:
            schema = await self.data_source_service.get_schema(data_source)
        except Exception as e:
            raise ValueError(f"Failed to fetch schema: {str(e)}")

        # 3. Generate SQL from natural language
        try:
            generated_sql = await self.nlp_service.generate_sql(
                natural_language_query, schema
            )
        except Exception as e:
            # Save failed query if requested
            if save:
                await self._save_query(
                    natural_language_query=natural_language_query,
                    data_source_id=data_source_id,
                    user_id=user_id,
                    name=name,
                    error_message=f"SQL generation failed: {str(e)}",
                )
            raise ValueError(f"Failed to generate SQL: {str(e)}")

        # 4. Execute the query
        try:
            rows, columns, execution_time_ms = (
                await self.data_source_service.execute_query(
                    data_source, generated_sql
                )
            )
        except Exception as e:
            # Save failed query
            if save:
                await self._save_query(
                    natural_language_query=natural_language_query,
                    generated_sql=generated_sql,
                    data_source_id=data_source_id,
                    user_id=user_id,
                    name=name,
                    error_message=f"Execution failed: {str(e)}",
                )
            raise ValueError(f"Query execution failed: {str(e)}")

        # 5. Process results
        total_rows = len(rows)
        truncated = total_rows > self.MAX_RESPONSE_ROWS
        if truncated:
            rows = rows[: self.MAX_RESPONSE_ROWS]

        # Serialize rows (handle non-JSON-serializable types)
        serialized_rows = self._serialize_rows(rows)

        # 6. Save to history if requested
        query_id = None
        if save:
            query_record = await self._save_query(
                natural_language_query=natural_language_query,
                generated_sql=generated_sql,
                data_source_id=data_source_id,
                user_id=user_id,
                name=name,
                execution_time_ms=execution_time_ms,
                result_rows_count=total_rows,
            )
            query_id = query_record.id

        return {
            "query_id": str(query_id) if query_id else None,
            "natural_language_query": natural_language_query,
            "generated_sql": generated_sql,
            "execution_time_ms": round(execution_time_ms, 2),
            "columns": columns,
            "rows": serialized_rows,
            "row_count": total_rows,
            "truncated": truncated,
        }

    async def _save_query(
        self,
        natural_language_query: str,
        data_source_id: UUID,
        user_id: UUID,
        name: Optional[str] = None,
        generated_sql: Optional[str] = None,
        execution_time_ms: Optional[float] = None,
        result_rows_count: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> Query:
        """Save a query to the database."""
        query = Query(
            natural_language_query=natural_language_query,
            generated_sql=generated_sql,
            execution_time_ms=execution_time_ms,
            result_rows_count=result_rows_count,
            error_message=error_message,
            name=name,
            user_id=user_id,
            data_source_id=data_source_id,
        )
        self.db.add(query)
        await self.db.flush()
        await self.db.refresh(query)
        return query

    def _serialize_rows(
        self, rows: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Serialize rows to JSON-safe types."""
        serialized = []
        for row in rows:
            clean_row = {}
            for key, value in row.items():
                if isinstance(value, datetime):
                    clean_row[key] = value.isoformat()
                elif isinstance(value, (int, float, str, bool, type(None))):
                    clean_row[key] = value
                else:
                    clean_row[key] = str(value)
            serialized.append(clean_row)
        return serialized

    # ==================== Query History ====================

    async def get_query_history(
        self,
        user_id: UUID,
        page: int = 1,
        per_page: int = 20,
    ) -> Tuple[List[Query], int]:
        """
        Get paginated query history for a user.

        Args:
            user_id: User ID
            page: Page number (1-indexed)
            per_page: Items per page

        Returns:
            Tuple of (queries, total_count)
        """
        # Get total count
        count_result = await self.db.execute(
            select(func.count(Query.id)).where(Query.user_id == user_id)
        )
        total = count_result.scalar_one()

        # Get paginated results
        offset = (page - 1) * per_page
        result = await self.db.execute(
            select(Query)
            .where(Query.user_id == user_id)
            .order_by(desc(Query.created_at))
            .offset(offset)
            .limit(per_page)
        )
        queries = list(result.scalars().all())

        return queries, total

    async def get_query_by_id(
        self, query_id: UUID, user_id: UUID
    ) -> Optional[Query]:
        """Get a specific query by ID, owned by user."""
        result = await self.db.execute(
            select(Query).where(
                Query.id == query_id,
                Query.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def update_query(
        self,
        query: Query,
        name: Optional[str] = None,
        is_favorite: Optional[bool] = None,
    ) -> Query:
        """Update query metadata."""
        if name is not None:
            query.name = name
        if is_favorite is not None:
            query.is_favorite = is_favorite
        await self.db.flush()
        await self.db.refresh(query)
        return query

    async def delete_query(self, query: Query) -> None:
        """Delete a query."""
        await self.db.delete(query)
        await self.db.flush()
