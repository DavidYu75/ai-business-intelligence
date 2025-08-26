"""
Main FastAPI application entry point for Real-Time BI Platform.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from typing import List

# Create FastAPI app instance
app = FastAPI(
    title="Real-Time Business Intelligence Platform",
    description="A comprehensive BI platform for natural language query processing and real-time data visualization",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
origins = os.getenv("BACKEND_CORS_ORIGINS", '["http://localhost:3000"]')
if isinstance(origins, str):
    origins = eval(origins)  # Convert string to list

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Real-Time Business Intelligence Platform API",
        "version": "0.1.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker health checks."""
    return {
        "status": "healthy",
        "service": "realtime-bi-backend",
        "version": "0.1.0"
    }

@app.get("/api/v1/health")
async def api_health_check():
    """API health check endpoint."""
    return {
        "status": "healthy",
        "api_version": "v1",
        "service": "realtime-bi-backend"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
