"""
API module for route registration.
"""

from fastapi import APIRouter

from app.api.auth import router as auth_router

# Create main API router
api_router = APIRouter()

# Include auth routes
api_router.include_router(auth_router)

__all__ = ["api_router"]
