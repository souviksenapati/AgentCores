"""
Authentication and authorization module for AgentCores
Provides JWT token handling, password verification, and role-based access control
"""

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.database import User, UserRole
from app.services import UserService, SecurityService

# Configuration
SECRET_KEY = "your-secret-key-here-change-in-production"  # Change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user with email and password"""
    user = UserService.get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    if not user.is_active:
        return None
    return user

async def get_current_user_from_token(token: str, db: Session) -> Optional[User]:
    """Get current user from JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    
    user = UserService.get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        return None
    
    # Update last activity
    UserService.update_last_activity(db, user_id)
    
    return user

# Authentication dependency
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user = await get_current_user_from_token(credentials.credentials, db)
    if user is None:
        raise credentials_exception
    
    return user

# Optional authentication dependency
async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, otherwise None"""
    try:
        user = await get_current_user_from_token(credentials.credentials, db)
        return user
    except:
        return None

# Tenant context dependency
def get_tenant_id(current_user: User = Depends(get_current_user)) -> str:
    """Get tenant ID from authenticated user"""
    return current_user.tenant_id

# Role-based access control decorators
def require_role(required_roles: list):
    """Decorator to require specific roles"""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {[role.value for role in required_roles]}"
            )
        return current_user
    return role_checker

# Convenience role checks
def require_owner_role(current_user: User = Depends(get_current_user)) -> User:
    """Require owner role"""
    if current_user.role != UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner role required"
        )
    return current_user

def require_admin_role(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role or higher"""
    if current_user.role not in [UserRole.OWNER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role or higher required"
        )
    return current_user

def require_manager_role(current_user: User = Depends(get_current_user)) -> User:
    """Require manager role or higher"""
    if current_user.role not in [UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager role or higher required"
        )
    return current_user

def require_developer_role(current_user: User = Depends(get_current_user)) -> User:
    """Require developer role or higher"""
    if current_user.role not in [UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.DEVELOPER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Developer role or higher required"
        )
    return current_user

def require_analyst_role(current_user: User = Depends(get_current_user)) -> User:
    """Require analyst role or higher"""
    if current_user.role not in [
        UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, 
        UserRole.DEVELOPER, UserRole.ANALYST
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Analyst role or higher required"
        )
    return current_user

def require_operator_role(current_user: User = Depends(get_current_user)) -> User:
    """Require operator role or higher"""
    if current_user.role not in [
        UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, 
        UserRole.DEVELOPER, UserRole.ANALYST, UserRole.OPERATOR
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operator role or higher required"
        )
    return current_user

def require_viewer_role(current_user: User = Depends(get_current_user)) -> User:
    """Require viewer role or higher (everyone except guest)"""
    if current_user.role == UserRole.GUEST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Viewer role or higher required"
        )
    return current_user

# Permission-based access control
def check_permission(required_permissions: list):
    """Check if user has required permissions based on role"""
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        # Define role permissions mapping
        role_permissions = {
            UserRole.OWNER: ["all"],
            UserRole.ADMIN: [
                "manage_users", "view_security", "manage_security", 
                "manage_agents", "view_analytics", "manage_settings"
            ],
            UserRole.MANAGER: [
                "view_security", "manage_agents", "view_analytics", 
                "manage_team", "view_reports"
            ],
            UserRole.DEVELOPER: [
                "create_agents", "view_agents", "manage_integrations", 
                "view_analytics", "deploy_agents"
            ],
            UserRole.ANALYST: [
                "view_analytics", "view_reports", "create_reports", 
                "view_agents", "view_tasks"
            ],
            UserRole.OPERATOR: [
                "view_monitoring", "manage_monitoring", "view_agents", 
                "manage_tasks", "view_logs"
            ],
            UserRole.VIEWER: [
                "view_dashboard", "view_agents", "view_tasks", 
                "view_basic_analytics"
            ],
            UserRole.GUEST: [
                "view_dashboard", "view_public_agents"
            ]
        }
        
        user_permissions = role_permissions.get(current_user.role, [])
        
        # Owner has all permissions
        if "all" in user_permissions:
            return current_user
        
        # Check if user has any of the required permissions
        if not any(perm in user_permissions for perm in required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {required_permissions}"
            )
        
        return current_user
    
    return permission_checker

# Security event logging middleware
async def log_security_event_middleware(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Middleware to log security events for sensitive operations"""
    # Get client IP and user agent
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    
    # Log the access
    SecurityService.log_security_event(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        event_type="api_access",
        severity="info",
        ip_address=client_ip,
        user_agent=user_agent,
        event_data={
            "endpoint": str(request.url),
            "method": request.method,
            "user_role": current_user.role.value
        },
        result="granted",
        risk_score=5
    )
    
    return current_user