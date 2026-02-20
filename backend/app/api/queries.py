"""
Query API endpoints for natural language query processing.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query as QueryParam, status

from app.api.dependencies import CurrentUser, DbSession
from app.schemas.query import (
    QueryCreate,
    QueryExecute,
    QueryExecuteResult,
    QueryHistory,
    QueryResponse,
    QueryUpdate,
)
from app.services.query_executor import QueryExecutor

router = APIRouter(prefix="/queries", tags=["Queries"])


@router.post(
    "",
    response_model=QueryExecuteResult,
    status_code=status.HTTP_201_CREATED,
    summary="Execute natural language query",
)
async def create_and_execute_query(
    query_in: QueryCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> QueryExecuteResult:
    """
    Process a natural language query:
    1. Generate SQL from natural language using Claude
    2. Execute the SQL against the target data source
    3. Save to query history
    4. Return results

    - **natural_language_query**: Your question in plain English
    - **data_source_id**: Which database to query
    - **name**: Optional name to save this query as
    """
    executor = QueryExecutor(db)

    try:
        result = await executor.execute_nl_query(
            natural_language_query=query_in.natural_language_query,
            data_source_id=query_in.data_source_id,
            user_id=current_user.id,
            save=True,
            name=query_in.name,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return QueryExecuteResult(**result)


@router.post(
    "/execute",
    response_model=QueryExecuteResult,
    summary="Execute query without saving",
)
async def execute_query(
    query_in: QueryExecute,
    db: DbSession,
    current_user: CurrentUser,
) -> QueryExecuteResult:
    """
    Execute a natural language query without saving to history.

    Useful for ad-hoc exploration.
    """
    executor = QueryExecutor(db)

    try:
        result = await executor.execute_nl_query(
            natural_language_query=query_in.natural_language_query,
            data_source_id=query_in.data_source_id,
            user_id=current_user.id,
            save=False,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return QueryExecuteResult(**result)


@router.get(
    "",
    response_model=QueryHistory,
    summary="Get query history",
)
async def get_query_history(
    db: DbSession,
    current_user: CurrentUser,
    page: int = QueryParam(default=1, ge=1, description="Page number"),
    per_page: int = QueryParam(default=20, ge=1, le=100, description="Items per page"),
) -> QueryHistory:
    """
    Get paginated query history for the current user.
    """
    executor = QueryExecutor(db)
    queries, total = await executor.get_query_history(
        user_id=current_user.id,
        page=page,
        per_page=per_page,
    )

    return QueryHistory(
        queries=[QueryResponse.model_validate(q) for q in queries],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get(
    "/{query_id}",
    response_model=QueryResponse,
    summary="Get specific query",
)
async def get_query(
    query_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> QueryResponse:
    """
    Get a specific query by ID.
    """
    executor = QueryExecutor(db)
    query = await executor.get_query_by_id(query_id, current_user.id)

    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found",
        )

    return QueryResponse.model_validate(query)


@router.patch(
    "/{query_id}",
    response_model=QueryResponse,
    summary="Update query",
)
async def update_query(
    query_id: UUID,
    query_update: QueryUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> QueryResponse:
    """
    Update query metadata (name, favorite status).
    """
    executor = QueryExecutor(db)
    query = await executor.get_query_by_id(query_id, current_user.id)

    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found",
        )

    query = await executor.update_query(
        query,
        name=query_update.name,
        is_favorite=query_update.is_favorite,
    )

    return QueryResponse.model_validate(query)


@router.delete(
    "/{query_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete query",
)
async def delete_query(
    query_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    """
    Delete a query from history.
    """
    executor = QueryExecutor(db)
    query = await executor.get_query_by_id(query_id, current_user.id)

    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found",
        )

    await executor.delete_query(query)
