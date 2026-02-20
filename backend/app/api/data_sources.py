"""
Data Sources API endpoints for managing database connections.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import CurrentUser, DbSession
from app.models.data_source import DataSourceType
from app.schemas.data_source import (
    DataSourceCreate,
    DataSourceResponse,
    DataSourceTestConnection,
    DataSourceTestResult,
    DataSourceUpdate,
)
from app.services.database_adapter import DataSourceService

router = APIRouter(prefix="/data-sources", tags=["Data Sources"])


# ==================== Schema Endpoints ====================


class SchemaResponse:
    """Response model for schema information."""
    pass


# ==================== Endpoints ====================


@router.post(
    "",
    response_model=DataSourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create data source",
)
async def create_data_source(
    data_source_in: DataSourceCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> DataSourceResponse:
    """
    Create a new data source connection.

    - **name**: Display name for the data source
    - **type**: Database type (postgresql, mysql, sqlite, csv)
    - **organization_id**: Organization that owns this data source
    - **host**: Database host (for postgresql/mysql)
    - **port**: Database port
    - **database**: Database name
    - **username**: Database username
    - **password**: Database password (stored encrypted)
    """
    service = DataSourceService(db)

    # Create the data source
    data_source = await service.create_data_source(
        name=data_source_in.name,
        type=data_source_in.type,
        description=data_source_in.description,
        organization_id=data_source_in.organization_id,
        host=data_source_in.host,
        port=data_source_in.port,
        database=data_source_in.database,
        username=data_source_in.username,
        password=data_source_in.password,
        file_path=data_source_in.file_path,
    )

    return DataSourceResponse.model_validate(data_source)


@router.get(
    "",
    response_model=List[DataSourceResponse],
    summary="List data sources",
)
async def list_data_sources(
    organization_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> List[DataSourceResponse]:
    """
    List all data sources for an organization.

    - **organization_id**: Filter by organization
    """
    service = DataSourceService(db)
    data_sources = await service.get_data_sources_by_org(organization_id)
    return [DataSourceResponse.model_validate(ds) for ds in data_sources]


@router.get(
    "/{data_source_id}",
    response_model=DataSourceResponse,
    summary="Get data source",
)
async def get_data_source(
    data_source_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> DataSourceResponse:
    """
    Get a specific data source by ID.
    """
    service = DataSourceService(db)
    data_source = await service.get_data_source(data_source_id)

    if not data_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found",
        )

    return DataSourceResponse.model_validate(data_source)


@router.patch(
    "/{data_source_id}",
    response_model=DataSourceResponse,
    summary="Update data source",
)
async def update_data_source(
    data_source_id: UUID,
    data_source_update: DataSourceUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> DataSourceResponse:
    """
    Update a data source's configuration.
    """
    service = DataSourceService(db)
    data_source = await service.get_data_source(data_source_id)

    if not data_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found",
        )

    # Update fields
    update_data = data_source_update.model_dump(exclude_unset=True)
    data_source = await service.update_data_source(data_source, **update_data)

    return DataSourceResponse.model_validate(data_source)


@router.delete(
    "/{data_source_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete data source",
)
async def delete_data_source(
    data_source_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    """
    Delete a data source.
    """
    service = DataSourceService(db)
    data_source = await service.get_data_source(data_source_id)

    if not data_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found",
        )

    await service.delete_data_source(data_source)


@router.post(
    "/test",
    response_model=DataSourceTestResult,
    summary="Test connection",
)
async def test_connection(
    test_params: DataSourceTestConnection,
    db: DbSession,
    current_user: CurrentUser,
) -> DataSourceTestResult:
    """
    Test a database connection without saving it.

    Useful for validating connection parameters before creating a data source.
    """
    service = DataSourceService(db)

    success, message, latency = await service.test_connection(
        type=test_params.type,
        host=test_params.host,
        port=test_params.port,
        database=test_params.database,
        username=test_params.username,
        password=test_params.password,
    )

    return DataSourceTestResult(
        success=success,
        message=message,
        latency_ms=latency,
    )


@router.post(
    "/{data_source_id}/test",
    response_model=DataSourceTestResult,
    summary="Test existing connection",
)
async def test_existing_connection(
    data_source_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> DataSourceTestResult:
    """
    Test an existing data source's connection.
    """
    service = DataSourceService(db)
    data_source = await service.get_data_source(data_source_id)

    if not data_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found",
        )

    success, message, latency = await service.test_connection(data_source=data_source)

    return DataSourceTestResult(
        success=success,
        message=message,
        latency_ms=latency,
    )


@router.get(
    "/{data_source_id}/schema",
    summary="Get database schema",
)
async def get_schema(
    data_source_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    refresh: bool = False,
) -> dict:
    """
    Get the schema (tables, columns, types) for a data source.

    - **refresh**: If true, bypass cache and fetch fresh schema
    """
    service = DataSourceService(db)
    data_source = await service.get_data_source(data_source_id)

    if not data_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found",
        )

    # Clear cache if refresh requested
    if refresh:
        data_source.schema_cache = None
        await db.flush()

    try:
        schema = await service.get_schema(data_source)
        return {"data_source_id": str(data_source_id), "schema": schema}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve schema: {str(e)}",
        )
