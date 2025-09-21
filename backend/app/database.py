from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://agent_user:agent_password@localhost:5432/agentcores_db")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=os.getenv("ENVIRONMENT") == "development"
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database with tables and default data"""
    print("🔧 Initializing multi-tenant database...")
    
    # Import models to ensure they're registered with Base
    from app.models.database import (
        Tenant, User, Agent, Task, TaskExecution, 
        TenantInvitation, AuditLog
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    # Create default tenant and admin user
    db = SessionLocal()
    try:
        # Check if we already have data
        existing_tenant_count = db.execute(text("SELECT COUNT(*) FROM tenants")).scalar()
        if existing_tenant_count > 0:
            print("ℹ️  Database already has data, skipping initialization")
            return
        
        # Generate IDs
        tenant_id = str(uuid.uuid4())
        admin_id = str(uuid.uuid4())
        
        # Create default tenant (using correct column names from the model)
        db.execute(text("""
            INSERT INTO tenants (id, name, subdomain, subscription_tier, contact_email, contact_name, status, created_at, updated_at)
            VALUES (:tenant_id, 'AgentCores Demo', 'demo', 'PROFESSIONAL', 'admin@demo.agentcores.com', 'Demo Admin', 'ACTIVE', :now, :now)
        """), {
            'tenant_id': tenant_id,
            'now': datetime.utcnow()
        })
        
        # Create admin user (using correct column names from the model)
        password_hash = get_password_hash("admin123")
        db.execute(text("""
            INSERT INTO users (id, tenant_id, email, first_name, last_name, password_hash, role, is_active, created_at, updated_at)
            VALUES (:user_id, :tenant_id, 'admin@demo.agentcores.com', 'Demo', 'Administrator', :password_hash, 'ADMIN', true, :now, :now)
        """), {
            'user_id': admin_id,
            'tenant_id': tenant_id,
            'password_hash': password_hash,
            'now': datetime.utcnow()
        })
        
        # Create audit log entry
        log_id = str(uuid.uuid4())
        db.execute(text("""
            INSERT INTO audit_logs (id, tenant_id, user_id, action, resource_type, resource_id, timestamp)
            VALUES (:log_id, :tenant_id, :admin_id, 'SYSTEM_INIT', 'DATABASE', 'system', :now)
        """), {
            'log_id': log_id,
            'tenant_id': tenant_id,
            'admin_id': admin_id,
            'now': datetime.utcnow()
        })
        
        db.commit()
        
        print("✅ Default tenant and admin user created")
        print("   Organization: AgentCores Demo")
        print("   Subdomain: demo")  
        print("   Email: admin@demo.agentcores.com")
        print("   Password: admin123")
        print("   ⚠️  Change password after first login!")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()