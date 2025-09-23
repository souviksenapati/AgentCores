from fastapi import FastAPI, Depends, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
import os
from datetime import datetime
from typing import Optional

from app.database import engine, get_db, Base
from app.models.database import *  # Import all models to register them with Base
from app.api.agents import router as agents_router
from app.api.auth import router as auth_router
from app.api.security import router as security_router
from app.schemas import HealthCheck
from app.services.agent_service import TenantService

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="AgentCores API",
    description="AI Agent Management Platform - Phase 1 MVP",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simplified middleware for single-domain architecture
@app.middleware("http")
async def tenant_middleware(request: Request, call_next):
    """Single-domain tenant context middleware"""
    # Skip middleware for health checks and docs
    if request.url.path in ["/", "/docs", "/redoc", "/openapi.json"] or request.url.path.startswith("/api/v1/health"):
        response = await call_next(request)
        return response
    
    # For single-domain architecture, tenant context is managed through authentication
    # No subdomain extraction needed - tenant context comes from JWT token
    response = await call_next(request)
    return response

# Include routers
app.include_router(
    agents_router,
    prefix="/api/v1",
    tags=["agents"]
)

app.include_router(
    auth_router,
    prefix="/api/v1",
    tags=["authentication", "tenant-management", "user-management"]
)

app.include_router(
    security_router,
    prefix="/api/v1",
    tags=["security"]
)

@app.get("/", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    return HealthCheck(
        status="healthy",
        timestamp=datetime.utcnow()
    )

@app.get("/api/v1/health", response_model=HealthCheck)
async def api_health_check():
    """API health check endpoint"""
    return HealthCheck(
        status="healthy",
        timestamp=datetime.utcnow()
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )