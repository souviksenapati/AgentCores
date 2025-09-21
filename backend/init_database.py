#!/usr/bin/env python3
"""
AgentCores Database Initialization Script

This script initializes a fresh multi-tenant database.
"""

import asyncio
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from app.database import engine, get_db, get_password_hash
    from app.models.database import Base
    from sqlalchemy import text
    from sqlalchemy.orm import Session
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   Make sure you're running this from the backend directory")
    print("   and all dependencies are installed")
    sys.exit(1)

async def create_tables():
    """Create all database tables"""
    print("🔧 Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully")

def create_default_tenant_and_admin():
    """Create a default tenant and admin user for initial setup"""
    print("👥 Creating default tenant and admin user...")
    
    # Generate IDs
    tenant_id = str(uuid.uuid4())
    admin_id = str(uuid.uuid4())
    
    with Session(engine) as db:
        # Create default tenant
        db.execute(text("""
            INSERT INTO tenants (id, name, subdomain, subscription_tier, contact_email, contact_name, is_active, created_at, updated_at)
            VALUES (:tenant_id, 'AgentCores Demo', 'demo', 'professional', 'admin@demo.agentcores.com', 'Demo Admin', true, :now, :now)
        """), {
            'tenant_id': tenant_id,
            'now': datetime.utcnow()
        })
        
        # Create admin user
        password_hash = get_password_hash("admin123")
        db.execute(text("""
            INSERT INTO users (id, tenant_id, email, full_name, hashed_password, role, is_active, created_at, updated_at)
            VALUES (:user_id, :tenant_id, 'admin@demo.agentcores.com', 'Demo Administrator', :password_hash, 'owner', true, :now, :now)
        """), {
            'user_id': admin_id,
            'tenant_id': tenant_id,
            'password_hash': password_hash,
            'now': datetime.utcnow()
        })
        
        # Create audit log entry
        log_id = str(uuid.uuid4())
        db.execute(text("""
            INSERT INTO audit_logs (id, tenant_id, user_id, action, resource_type, details, created_at)
            VALUES (:log_id, :tenant_id, :admin_id, 'SYSTEM_INIT', 'DATABASE', :details, :now)
        """), {
            'log_id': log_id,
            'tenant_id': tenant_id,
            'admin_id': admin_id,
            'details': '{"action": "database_initialization", "timestamp": "' + datetime.utcnow().isoformat() + '"}',
            'now': datetime.utcnow()
        })
        
        db.commit()
    
    print("✅ Default tenant and admin user created")
    print(f"   Organization: AgentCores Demo")
    print(f"   Subdomain: demo")
    print(f"   Admin Email: admin@demo.agentcores.com")
    print(f"   Admin Password: admin123")
    print("   ⚠️  Change the password after first login!")

async def main():
    """Main initialization function"""
    print("🚀 AgentCores Database Initialization")
    print("=" * 50)
    
    try:
        # Create tables
        await create_tables()
        
        # Create default data
        create_default_tenant_and_admin()
        
        print("\n🎉 Database initialization completed successfully!")
        print("\n🌐 Next steps:")
        print("   1. Start the application: docker-compose up -d")
        print("   2. Access frontend: http://localhost:3000")
        print("   3. Login with admin@demo.agentcores.com / admin123")
        print("   4. Change the default password")
        print("   5. Create your first agent!")
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    asyncio.run(main())