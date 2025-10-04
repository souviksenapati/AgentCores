# Test configuration for AgentCores backend
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_org_db, get_individual_db

# Test database URL
TEST_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test_agentcores.db")

# Create test engine
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in TEST_DATABASE_URL else {},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_org_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_individual_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override dependencies for testing
app.dependency_overrides[get_org_db] = override_get_org_db
app.dependency_overrides[get_individual_db] = override_get_individual_db


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def db():
    """Database fixture"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Set up test environment variables"""
    monkeypatch.setenv("SECRET_KEY", "test_secret_key")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test_api_key")
    monkeypatch.setenv("DATABASE_URL", TEST_DATABASE_URL)
