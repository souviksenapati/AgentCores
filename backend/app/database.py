"""
Enterprise Database Configuration & Connection Management
Built for MVP simplicity, designed for billion-dollar platform scale.
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from passlib.context import CryptContext
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class EnterpriseConfig:
    """
    Enterprise Configuration Management

    Current: Environment-based configuration
    Future: Dynamic configuration, secrets management, feature flags
    """

    # Environment & Deployment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Application
    APP_NAME: str = os.getenv("APP_NAME", "AgentCores")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    APP_DESCRIPTION: str = os.getenv(
        "APP_DESCRIPTION", "AI Agent Orchestration Platform"
    )

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    WORKERS: int = int(os.getenv("WORKERS", "4"))

    # Multi-Database Configuration (Legacy database removed)
    ORG_DATABASE_URL: str = os.getenv(
        "ORG_DATABASE_URL",
        "postgresql://agent_user:agent_password@postgres-orgs:5432/agentcores_orgs",
    )
    INDIVIDUAL_DATABASE_URL: str = os.getenv(
        "INDIVIDUAL_DATABASE_URL",
        "postgresql://agent_user:agent_password@postgres-individuals:5432/agentcores_individuals",
    )

    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "20"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "30"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_POOL_SIZE: int = int(os.getenv("REDIS_POOL_SIZE", "20"))

    # Security
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "your-super-secret-jwt-key-change-in-production"
    )
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480")
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))

    # CORS & Security Headers
    ALLOWED_HOSTS: list = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    CORS_CREDENTIALS: bool = os.getenv("CORS_CREDENTIALS", "true").lower() == "true"

    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = int(
        os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "100")
    )
    RATE_LIMIT_BURST: int = int(os.getenv("RATE_LIMIT_BURST", "200"))

    # AI Providers
    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_SITE_URL: str = os.getenv(
        "OPENROUTER_SITE_URL", "https://agentcores.com"
    )
    OPENROUTER_SITE_NAME: str = os.getenv("OPENROUTER_SITE_NAME", "AgentCores")

    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_ORG_ID: Optional[str] = os.getenv("OPENAI_ORG_ID")

    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")

    # Multi-tenancy
    DEFAULT_TENANT_ID: str = os.getenv("DEFAULT_TENANT_ID", "default")
    DEFAULT_TENANT_NAME: str = os.getenv("DEFAULT_TENANT_NAME", "Default Organization")
    DEFAULT_MAX_AGENTS: int = int(os.getenv("DEFAULT_MAX_AGENTS", "10"))
    DEFAULT_MAX_TASKS_PER_HOUR: int = int(
        os.getenv("DEFAULT_MAX_TASKS_PER_HOUR", "1000")
    )
    DEFAULT_MAX_MONTHLY_COST: float = float(
        os.getenv("DEFAULT_MAX_MONTHLY_COST", "1000.0")
    )

    # Task Execution
    MAX_CONCURRENT_TASKS: int = int(os.getenv("MAX_CONCURRENT_TASKS", "10"))
    TASK_TIMEOUT_SECONDS: int = int(os.getenv("TASK_TIMEOUT_SECONDS", "300"))
    MAX_TASK_RETRIES: int = int(os.getenv("MAX_TASK_RETRIES", "3"))
    TASK_CLEANUP_INTERVAL_MINUTES: int = int(
        os.getenv("TASK_CLEANUP_INTERVAL_MINUTES", "60")
    )

    # Event Service
    EVENT_STORE_ENABLED: bool = (
        os.getenv("EVENT_STORE_ENABLED", "true").lower() == "true"
    )
    EVENT_STORE_MAX_EVENTS: int = int(os.getenv("EVENT_STORE_MAX_EVENTS", "10000"))
    EVENT_RETENTION_HOURS: int = int(os.getenv("EVENT_RETENTION_HOURS", "168"))
    EVENT_ASYNC_PROCESSING: bool = (
        os.getenv("EVENT_ASYNC_PROCESSING", "true").lower() == "true"
    )

    # Monitoring
    METRICS_ENABLED: bool = os.getenv("METRICS_ENABLED", "true").lower() == "true"
    PROMETHEUS_PORT: int = int(os.getenv("PROMETHEUS_PORT", "9090"))
    HEALTH_CHECK_ENABLED: bool = (
        os.getenv("HEALTH_CHECK_ENABLED", "true").lower() == "true"
    )
    HEALTH_CHECK_INTERVAL: int = int(os.getenv("HEALTH_CHECK_INTERVAL", "60"))

    # Enterprise Features
    COMPLIANCE_MODE: str = os.getenv("COMPLIANCE_MODE", "basic")
    AUDIT_LOGGING: bool = os.getenv("AUDIT_LOGGING", "true").lower() == "true"
    DATA_ENCRYPTION_AT_REST: bool = (
        os.getenv("DATA_ENCRYPTION_AT_REST", "false").lower() == "true"
    )

    # Feature Flags
    FEATURE_MULTI_TENANCY: bool = (
        os.getenv("FEATURE_MULTI_TENANCY", "true").lower() == "true"
    )
    FEATURE_ANALYTICS: bool = os.getenv("FEATURE_ANALYTICS", "true").lower() == "true"
    FEATURE_ADVANCED_TEMPLATES: bool = (
        os.getenv("FEATURE_ADVANCED_TEMPLATES", "true").lower() == "true"
    )
    FEATURE_MULTI_PROVIDER: bool = (
        os.getenv("FEATURE_MULTI_PROVIDER", "true").lower() == "true"
    )
    FEATURE_COST_TRACKING: bool = (
        os.getenv("FEATURE_COST_TRACKING", "true").lower() == "true"
    )

    # Cost Management
    MONTHLY_COST_ALERT_THRESHOLD: float = float(
        os.getenv("MONTHLY_COST_ALERT_THRESHOLD", "800.0")
    )
    DAILY_COST_ALERT_THRESHOLD: float = float(
        os.getenv("DAILY_COST_ALERT_THRESHOLD", "50.0")
    )
    COST_TRACKING_ENABLED: bool = (
        os.getenv("COST_TRACKING_ENABLED", "true").lower() == "true"
    )

    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment"""
        return cls.ENVIRONMENT.lower() == "production"

    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development environment"""
        return cls.ENVIRONMENT.lower() == "development"

    @classmethod
    def get_database_config(cls) -> Dict[str, Any]:
        """Get database configuration for SQLAlchemy (multi-tenant setup)"""
        config = {
            "pool_size": cls.DB_POOL_SIZE,
            "max_overflow": cls.DB_MAX_OVERFLOW,
            "pool_timeout": cls.DB_POOL_TIMEOUT,
            "pool_recycle": cls.DB_POOL_RECYCLE,
            "pool_pre_ping": True,
            "echo": cls.DEBUG,
        }

        # Enterprise: Add SSL configuration for production
        if cls.is_production():
            config["connect_args"] = {"sslmode": "require"}

        return config

    @classmethod
    def get_cors_config(cls) -> Dict[str, Any]:
        """Get CORS configuration"""
        return {
            "allow_origins": cls.CORS_ORIGINS,
            "allow_credentials": cls.CORS_CREDENTIALS,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            "allow_headers": ["*"],
            "expose_headers": ["X-Tenant-ID", "X-Request-ID"],
        }

    @classmethod
    def validate_configuration(cls) -> Dict[str, Any]:
        """Validate enterprise configuration"""
        issues = []
        warnings = []

        # Critical validations
        if (
            not cls.SECRET_KEY
            or cls.SECRET_KEY == "your-super-secret-jwt-key-change-in-production"
        ):
            issues.append("SECRET_KEY must be set to a secure value in production")

        if cls.is_production() and cls.DEBUG:
            issues.append("DEBUG should be False in production")

        if (
            not cls.OPENROUTER_API_KEY
            and not cls.OPENAI_API_KEY
            and not cls.ANTHROPIC_API_KEY
        ):
            issues.append("At least one AI provider API key must be configured")

        # Warnings
        if cls.ACCESS_TOKEN_EXPIRE_MINUTES > 1440:  # 24 hours
            warnings.append(
                "ACCESS_TOKEN_EXPIRE_MINUTES is very long, consider shorter duration"
            )

        if not cls.FEATURE_COST_TRACKING:
            warnings.append(
                "Cost tracking is disabled - consider enabling for enterprise use"
            )

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "environment": cls.ENVIRONMENT,
            "features_enabled": {
                "multi_tenancy": cls.FEATURE_MULTI_TENANCY,
                "analytics": cls.FEATURE_ANALYTICS,
                "cost_tracking": cls.FEATURE_COST_TRACKING,
                "multi_provider": cls.FEATURE_MULTI_PROVIDER,
            },
        }


# Initialize configuration
config = EnterpriseConfig()

# Create multi-tenant database engines
db_config = config.get_database_config()

# Organization database engine
org_engine = create_engine(
    config.ORG_DATABASE_URL, **{k: v for k, v in db_config.items() if k != "url"}
)

# Individual users database engine
individual_engine = create_engine(
    config.INDIVIDUAL_DATABASE_URL, **{k: v for k, v in db_config.items() if k != "url"}
)

# Create SessionLocal classes for each database
OrgSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=org_engine)
IndividualSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=individual_engine
)

# Base class for models
Base = declarative_base()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# Multi-Database Session Management
def get_db_session(account_type: str):
    """
    Get database session based on account type

    Args:
        account_type: "individual" or "organization"

    Returns:
        Database session for the appropriate database
    """
    if account_type == "individual":
        return IndividualSessionLocal()
    elif account_type == "organization":
        return OrgSessionLocal()
    else:
        raise ValueError(
            f"Invalid account type: {account_type}. Must be 'individual' or 'organization'"
        )


def get_db():
    """
    FastAPI dependency for database session.
    Defaults to organization database for backwards compatibility.
    """
    db = OrgSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependency to get Organization DB session
def get_org_db():
    db = OrgSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependency to get Individual DB session
def get_individual_db():
    db = IndividualSessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """Initialize multi-database setup with tables and default data"""
    print("🔧 Initializing enterprise multi-database system...")
    print("   📊 Organization Database: For multi-tenant organizations")
    print("   👤 Individual Database: For isolated individual users")
    print("   🔄 Legacy Database: For compatibility and fallback")

    # Validate configuration first
    validation = config.validate_configuration()
    if not validation["valid"]:
        print("❌ Configuration validation failed:")
        for issue in validation["issues"]:
            print(f"   • {issue}")
        raise RuntimeError("Invalid configuration")

    if validation["warnings"]:
        print("⚠️  Configuration warnings:")
        for warning in validation["warnings"]:
            print(f"   • {warning}")

    # Import models to ensure they're registered with Base

    # Create tables in multi-tenant databases
    print("🏢 Creating organization database tables...")
    Base.metadata.create_all(bind=org_engine, checkfirst=True)

    print("👤 Creating individual users database tables...")
    Base.metadata.create_all(bind=individual_engine, checkfirst=True)

    print("✅ Multi-tenant database tables created")

    # Create default data in organization database
    db = OrgSessionLocal()
    try:
        # Check if we already have data
        existing_tenant_count = db.execute(
            text("SELECT COUNT(*) FROM tenants")
        ).scalar()
        if existing_tenant_count and existing_tenant_count > 0:
            print("ℹ️  Database already has data, skipping initialization")
            return

        # Create default tenant
        tenant_id = config.DEFAULT_TENANT_ID
        db.execute(
            text(
                """
            INSERT INTO tenants (
                tenant_id, name, description, status, tier, compliance_level,
                max_agents, max_tasks_per_hour, max_monthly_cost,
                billing_plan, created_at, updated_at
            )
            VALUES (
                :tenant_id, :name, :description, 'active', 'basic', 'basic',
                :max_agents, :max_tasks_per_hour, :max_monthly_cost,
                'pay_as_you_go', :now, :now
            )
        """
            ),
            {
                "tenant_id": tenant_id,
                "name": config.DEFAULT_TENANT_NAME,
                "description": "Default tenant for AgentCores MVP",
                "max_agents": config.DEFAULT_MAX_AGENTS,
                "max_tasks_per_hour": config.DEFAULT_MAX_TASKS_PER_HOUR,
                "max_monthly_cost": config.DEFAULT_MAX_MONTHLY_COST,
                "now": datetime.utcnow(),
            },
        )

        # Create default templates
        templates = [
            {
                "template_id": "customer_service_basic",
                "name": "Customer Service Assistant",
                "description": "AI agent for handling customer inquiries and support",
                "industry": "customer_service",
                "category": "conversational",
                "config": '{"model": "anthropic/claude-3-haiku", "temperature": 0.7, "max_tokens": 1000}',
                "approved_for_production": True,
                "created_by": "system",
            },
            {
                "template_id": "sales_assistant_basic",
                "name": "Sales Assistant",
                "description": "AI agent for sales support and lead qualification",
                "industry": "sales",
                "category": "conversational",
                "config": '{"model": "anthropic/claude-3-sonnet", "temperature": 0.8, "max_tokens": 1200}',
                "approved_for_production": True,
                "created_by": "system",
            },
        ]

        for template in templates:
            db.execute(
                text(
                    """
                INSERT INTO templates (
                    template_id, name, description, industry, category, config,
                    approved_for_production, created_by, created_at, updated_at
                )
                VALUES (
                    :template_id, :name, :description, :industry, :category, :config,
                    :approved_for_production, :created_by, :now, :now
                )
            """
                ),
                {**template, "now": datetime.utcnow()},
            )

        db.commit()

        print("✅ Enterprise initialization complete")
        print(f"   Default Tenant: {config.DEFAULT_TENANT_NAME}")
        print(f"   Tenant ID: {tenant_id}")
        print(f"   Environment: {config.ENVIRONMENT}")
        print(f"   Features: {list(validation['features_enabled'].keys())}")
        print("   📋 Default templates created")

    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


# Global configuration instance
config = EnterpriseConfig()


def validate_startup_configuration():
    """Validate startup configuration for Docker deployment"""
    try:
        config = EnterpriseConfig()

        # Basic validation
        required_settings = [
            "ORG_DATABASE_URL",
            "INDIVIDUAL_DATABASE_URL",
            "SECRET_KEY",
        ]
        missing = [
            setting
            for setting in required_settings
            if not getattr(config, setting, None)
        ]

        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")

        # Test database connections
        with org_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        with individual_engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        print("✅ Startup configuration validated")
        print(f"   Environment: {config.ENVIRONMENT}")
        print("   Database: Connected")
        return True

    except Exception as e:
        print(f"❌ Startup validation failed: {e}")
        raise
