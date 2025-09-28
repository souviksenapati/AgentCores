from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import timedelta

from app.database import get_db
from app.auth import (
    authenticate_user, create_access_token, get_current_user, get_password_hash,
    get_tenant_id, require_admin_role, require_manager_role, ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.models.database import User, Tenant, UserRole
# TODO: Import actual services when they are implemented

router = APIRouter()

# Pydantic Models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    tenant_name: Optional[str] = None

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict

class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    role: str
    tenant_id: str
    is_active: bool
    last_login: Optional[str] = None

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserInvite(BaseModel):
    email: EmailStr
    role: UserRole

# Authentication Endpoints
@router.post("/auth/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Authenticate user and return access token"""
    user = authenticate_user(db, login_data.email, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    
    # Update last login
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.commit()
    
    # TODO: Add security event logging
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role.value,
            "tenant_id": user.tenant_id,
            "is_active": user.is_active,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
    )

@router.post("/auth/logout", status_code=204)
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout user (client should discard tokens)"""
    # TODO: Add security event logging
    
    return

# User Management Endpoints
@router.get("/users", response_model=List[UserResponse])
async def get_users(
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all users in tenant"""
    users = db.query(User).filter(
        User.tenant_id == tenant_id,
        User.is_active == True
    ).all()
    
    return [
        UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role.value,
            tenant_id=user.tenant_id,
            is_active=user.is_active,
            last_login=user.last_login.isoformat() if user.last_login else None
        ) for user in users
    ]

@router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role.value,
        tenant_id=current_user.tenant_id,
        is_active=current_user.is_active,
        last_login=current_user.last_login.isoformat() if current_user.last_login else None
    )

@router.put("/users/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    # Users can only update their own name, not role or active status
    if user_data.first_name is not None:
        current_user.first_name = user_data.first_name
    if user_data.last_name is not None:
        current_user.last_name = user_data.last_name
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role.value,
        tenant_id=current_user.tenant_id,
        is_active=current_user.is_active,
        last_login=current_user.last_login.isoformat() if current_user.last_login else None
    )

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(require_admin_role),
    db: Session = Depends(get_db)
):
    """Update user information (admin only)"""
    user = db.query(User).filter(
        User.id == user_id,
        User.tenant_id == tenant_id
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Admin can update all fields
    if user_data.first_name is not None:
        user.first_name = user_data.first_name
    if user_data.last_name is not None:
        user.last_name = user_data.last_name
    if user_data.role is not None:
        user.role = user_data.role
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    db.commit()
    db.refresh(user)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role.value,
        tenant_id=user.tenant_id,
        is_active=user.is_active,
        last_login=user.last_login.isoformat() if user.last_login else None
    )

# User Invitation Endpoints
@router.post("/invitations", status_code=201)
async def invite_user(
    invitation_data: UserInvite,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(require_manager_role),
    db: Session = Depends(get_db)
):
    """Invite a user to the tenant"""
    # TODO: Implement invitation service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Invitation feature not implemented yet"
    )