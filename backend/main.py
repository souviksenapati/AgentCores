from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
import os
from datetime import datetime

from app.database import engine, get_db
from app.models.database import Base
from app.api.agents import router as agents_router
from app.schemas import HealthCheck

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

# Include routers
app.include_router(
    agents_router,
    prefix="/api/v1",
    tags=["agents"]
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