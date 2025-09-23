"""
Demo Data Seeder for AgentCores Security Implementation
Creates demo organization, users, and security events for testing
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
from passlib.context import CryptContext

from app.models.database import (
    Tenant, User, UserRole, TenantStatus, TenantTier, 
    SecurityEvent, TenantInvitation, InvitationStatus
)
from app.database import SessionLocal

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def seed_demo_data():
    """Seed database with demo data"""
    db = SessionLocal()
    try:
        # Check if demo tenant already exists
        existing_tenant = db.query(Tenant).filter(Tenant.name == "AgentCores Demo").first()
        if existing_tenant:
            print("Demo data already exists. Skipping...")
            return
        
        # Create demo tenant
        demo_tenant = Tenant(
            id="demo-tenant-001",
            name="AgentCores Demo",
            description="Demo organization for AgentCores security testing",
            status=TenantStatus.ACTIVE,
            tier=TenantTier.ENTERPRISE,
            domain="demo.agentcores.com",
            billing_email="billing@demo.agentcores.com",
            max_agents=100,
            max_tasks_per_hour=10000,
            max_monthly_cost=10000.0,
            current_agents=8,
            current_month_tasks=1250,
            current_month_cost=485.75,
            session_timeout_minutes=30,
            require_mfa=False
        )
        db.add(demo_tenant)
        
        # Create demo users for each role
        demo_users = [
            {
                "email": "sarah.johnson@agentcores.com",
                "first_name": "Sarah",
                "last_name": "Johnson", 
                "role": UserRole.OWNER,
                "department": "Executive",
                "job_title": "CEO",
                "password": "owner123"
            },
            {
                "email": "michael.chen@agentcores.com",
                "first_name": "Michael",
                "last_name": "Chen",
                "role": UserRole.ADMIN,
                "department": "IT",
                "job_title": "IT Director",
                "password": "admin123"
            },
            {
                "email": "emily.rodriguez@agentcores.com",
                "first_name": "Emily",
                "last_name": "Rodriguez",
                "role": UserRole.MANAGER,
                "department": "Operations",
                "job_title": "Operations Manager",
                "password": "manager123"
            },
            {
                "email": "david.kim@agentcores.com",
                "first_name": "David",
                "last_name": "Kim",
                "role": UserRole.DEVELOPER,
                "department": "Engineering",
                "job_title": "Senior Developer",
                "password": "developer123"
            },
            {
                "email": "lisa.thompson@agentcores.com",
                "first_name": "Lisa",
                "last_name": "Thompson",
                "role": UserRole.ANALYST,
                "department": "Analytics",
                "job_title": "Data Analyst",
                "password": "analyst123"
            },
            {
                "email": "robert.martinez@agentcores.com",
                "first_name": "Robert",
                "last_name": "Martinez",
                "role": UserRole.OPERATOR,
                "department": "Operations",
                "job_title": "System Operator",
                "password": "operator123"
            },
            {
                "email": "jennifer.lee@agentcores.com",
                "first_name": "Jennifer",
                "last_name": "Lee",
                "role": UserRole.VIEWER,
                "department": "Marketing",
                "job_title": "Marketing Coordinator",
                "password": "viewer123"
            },
            {
                "email": "alex.wilson@external.com",
                "first_name": "Alex",
                "last_name": "Wilson",
                "role": UserRole.GUEST,
                "department": "External",
                "job_title": "External Consultant",
                "password": "guest123"
            }
        ]
        
        created_users = []
        for user_data in demo_users:
            user = User(
                tenant_id=demo_tenant.id,
                email=user_data["email"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                password_hash=hash_password(user_data["password"]),
                role=user_data["role"],
                department=user_data["department"],
                job_title=user_data["job_title"],
                is_active=True,
                is_verified=True,
                last_login=datetime.utcnow() - timedelta(minutes=30),
                last_activity=datetime.utcnow() - timedelta(minutes=15),
                timezone="UTC",
                language="en"
            )
            db.add(user)
            created_users.append(user)
        
        # Flush to get user IDs
        db.flush()
        
        # Create demo security events
        security_events = []
        
        # Recent login events
        for i, user in enumerate(created_users[:6]):  # Only for active users
            login_event = SecurityEvent(
                tenant_id=demo_tenant.id,
                user_id=user.id,
                event_type="login",
                severity="info",
                ip_address=f"192.168.1.{100 + i}",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                event_data={
                    "login_method": "password",
                    "success": True,
                    "user_role": user.role.value
                },
                result="success",
                risk_score=5,
                created_at=datetime.utcnow() - timedelta(minutes=30 - i * 2)
            )
            security_events.append(login_event)
        
        # Some failed login attempts
        failed_login_event = SecurityEvent(
            tenant_id=demo_tenant.id,
            event_type="failed_login",
            severity="warning",
            ip_address="203.0.113.42",
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            event_data={
                "attempted_email": "admin@agentcores.com",
                "failure_reason": "invalid_password",
                "attempt_count": 3
            },
            result="blocked",
            risk_score=45,
            created_at=datetime.utcnow() - timedelta(minutes=45)
        )
        security_events.append(failed_login_event)
        
        # Permission check events
        for user in created_users[:4]:  # Higher privilege users
            perm_event = SecurityEvent(
                tenant_id=demo_tenant.id,
                user_id=user.id,
                event_type="permission_check",
                severity="info",
                ip_address=f"192.168.1.{200 + hash(user.email) % 50}",
                event_data={
                    "requested_resource": "/api/v1/security/dashboard",
                    "granted": True,
                    "user_role": user.role.value
                },
                result="granted",
                risk_score=10,
                created_at=datetime.utcnow() - timedelta(minutes=20)
            )
            security_events.append(perm_event)
        
        # Suspicious activity (simulated)
        suspicious_event = SecurityEvent(
            tenant_id=demo_tenant.id,
            event_type="suspicious_activity",
            severity="warning",
            ip_address="198.51.100.23",
            user_agent="Python/3.9 requests/2.28.1",
            event_data={
                "activity_type": "automated_requests",
                "request_rate": "50/minute",
                "pattern": "unusual"
            },
            result="monitored",
            risk_score=75,
            threat_indicators=["high_request_rate", "non_browser_agent"],
            created_at=datetime.utcnow() - timedelta(hours=2)
        )
        security_events.append(suspicious_event)
        
        # Add all security events
        for event in security_events:
            db.add(event)
        
        # Commit all changes
        db.commit()
        
        print("✅ Demo data seeded successfully!")
        print(f"Demo Tenant: {demo_tenant.name} (ID: {demo_tenant.id})")
        print(f"Created {len(created_users)} demo users")
        print(f"Created {len(security_events)} security events")
        print("\n🔐 Demo Login Credentials:")
        print("=" * 50)
        for user_data in demo_users:
            print(f"{user_data['role'].value.upper():<12} | {user_data['email']:<35} | {user_data['password']}")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error seeding demo data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🌱 Seeding demo data...")
    seed_demo_data()