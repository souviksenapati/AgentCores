from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.services.agent_service import AuthService
from app.models.database import User

# Authentication setup
security = HTTPBearer()

# Authentication dependency
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(credentials.credentials)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

# Optional authentication dependency (for public endpoints that can work with or without auth)
async def get_current_user_optional(
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, otherwise None"""
    try:
        # This would need to be called differently since we don't have request here
        # For now, return None - this is mainly for public endpoints
        return None
    except:
        return None

# Tenant context dependency - now gets from JWT token
def get_tenant_id(current_user: User = Depends(get_current_user)) -> str:
    """Get tenant ID from authenticated user"""
    return current_user.tenant_id

# Role-based access control
def require_admin_role(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role"""
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required"
        )
    return current_user

def require_admin_or_member_role(current_user: User = Depends(get_current_user)) -> User:
    """Require admin or member role (not viewer)"""
    if current_user.role.value not in ["admin", "member"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or member role required"
        )
    return current_user