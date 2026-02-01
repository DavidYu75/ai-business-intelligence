"""
Query Pydantic schemas for request/response validation.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class QueryBase(BaseModel):
    """Base schema for Query."""

    natural_language_query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Natural language query text",
    )


class QueryCreate(QueryBase):
    """Schema for creating a new query."""

    data_source_id: uuid.UUID = Field(..., description="Target data source ID")
    name: Optional[str] = Field(None, max_length=255, description="Optional query name")


class QueryExecute(QueryBase):
    """Schema for executing a query without saving."""

    data_source_id: uuid.UUID = Field(..., description="Target data source ID")


class QueryUpdate(BaseModel):
    """Schema for updating query fields."""

    name: Optional[str] = Field(None, max_length=255, description="Updated name")
    is_favorite: Optional[bool] = Field(None, description="Favorite status")


class QueryResponse(QueryBase):
    """Schema for query response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Query ID")
    generated_sql: Optional[str] = Field(None, description="Generated SQL query")
    execution_time_ms: Optional[float] = Field(None, description="Execution time in ms")
    result_rows_count: Optional[int] = Field(None, description="Number of result rows")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    is_favorite: bool = Field(..., description="Favorite status")
    name: Optional[str] = Field(None, description="Query name")
    user_id: uuid.UUID = Field(..., description="Owner user ID")
    data_source_id: uuid.UUID = Field(..., description="Data source ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class QueryExecuteResult(BaseModel):
    """Schema for query execution result."""

    query_id: Optional[uuid.UUID] = Field(None, description="Query ID if saved")
    natural_language_query: str = Field(..., description="Original query")
    generated_sql: str = Field(..., description="Generated SQL")
    execution_time_ms: float = Field(..., description="Execution time in ms")
    columns: List[str] = Field(..., description="Result column names")
    rows: List[Dict[str, Any]] = Field(..., description="Result rows as dicts")
    row_count: int = Field(..., description="Total row count")
    truncated: bool = Field(False, description="Whether results were truncated")


class QueryHistory(BaseModel):
    """Schema for query history list."""

    queries: List[QueryResponse] = Field(..., description="List of queries")
    total: int = Field(..., description="Total count")
    page: int = Field(..., description="Current page")
    per_page: int = Field(..., description="Items per page")
