"""
Database utilities and dependency injection for FastAPI.

Provides the get_db dependency for route handlers.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database session injection.

    This is the primary dependency to use in route handlers for
    database access. It wraps get_async_session for cleaner imports.

    Yields:
        AsyncSession: Database session for the request.

    Example:
        @router.get("/users")
        async def list_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
    """
    async for session in get_async_session():
        yield session
