"""
API module for route registration.
"""

from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.data_sources import router as data_sources_router
from app.api.queries import router as queries_router

# Create main API router
api_router = APIRouter()

# Include routers
api_router.include_router(auth_router)
api_router.include_router(data_sources_router)
api_router.include_router(queries_router)

__all__ = ["api_router"]
