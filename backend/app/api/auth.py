from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas import (
    UserLogin, UserRegister, UserInviteAccept, TokenResponse, RefreshTokenRequest,
    UserResponse, UserUpdate, UserInvite, TenantCreate, TenantResponse, TenantUpdate,
    InvitationResponse
)
from app.services.agent_service import AuthService, TenantService
from app.auth import get_current_user, get_tenant_id, require_admin_role, require_admin_or_member_role
from app.models.database import User
from datetime import timedelta

router = APIRouter()

# Authentication Endpoints
@router.post("/auth/register", response_model=TokenResponse, status_code=201)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """Register a new user account"""
    try:
        # Get tenant by name instead of subdomain
        tenant_service = TenantService(db)
        tenant = await tenant_service.get_tenant_by_name(user_data.tenant_name)
        
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organization '{user_data.tenant_name}' not found"
            )
        
        # Register user
        auth_service = AuthService(db)
        user = await auth_service.register_user(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            tenant_id=tenant.id
        )
        
        # Generate tokens
        access_token = auth_service.create_access_token(
            data={"sub": user.id, "tenant_id": tenant.id, "role": user.role.value}
        )
        refresh_token = auth_service.create_refresh_token(
            data={"sub": user.id, "tenant_id": tenant.id}
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=1800,  # 30 minutes
            user=UserResponse.model_validate(user),
            tenant=TenantResponse.model_validate(tenant)
        )
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/auth/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Authenticate user and return tokens"""
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(
        email=login_data.email,
        password=login_data.password,
        tenant_name=login_data.tenant_name
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email, password, or organization"
        )
    
    # Get tenant info
    tenant_service = TenantService(db)
    tenant = await tenant_service.get_tenant_by_name(login_data.tenant_name)
    
    # Generate tokens
    access_token = auth_service.create_access_token(
        data={"sub": user.id, "tenant_id": user.tenant_id, "role": user.role.value}
    )
    refresh_token = auth_service.create_refresh_token(
        data={"sub": user.id, "tenant_id": user.tenant_id}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=1800,  # 30 minutes
        user=UserResponse.model_validate(user),
        tenant=TenantResponse.model_validate(tenant)
    )

@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token"""
    auth_service = AuthService(db)
    payload = auth_service.verify_token(refresh_data.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    tenant_id = payload.get("tenant_id")
    
    user = db.query(User).filter(
        User.id == user_id,
        User.tenant_id == tenant_id,
        User.is_active == True
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Generate new tokens
    access_token = auth_service.create_access_token(
        data={"sub": user.id, "tenant_id": user.tenant_id, "role": user.role.value}
    )
    refresh_token = auth_service.create_refresh_token(
        data={"sub": user.id, "tenant_id": user.tenant_id}
    )
    
    # Get tenant info
    tenant = db.query(User).join(User.tenant).filter(User.id == user_id).first().tenant
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=1800,  # 30 minutes
        user=UserResponse.model_validate(user),
        tenant=TenantResponse.model_validate(tenant)
    )

@router.post("/auth/logout", status_code=204)
async def logout(
    current_user: User = Depends(get_current_user)
):
    """Logout user (client should discard tokens)"""
    # In a full implementation, you would blacklist the token
    # For now, just return success - client should discard tokens
    return

# Tenant Management Endpoints
@router.post("/tenants", response_model=TenantResponse, status_code=201)
async def create_tenant(
    tenant_data: TenantCreate,
    db: Session = Depends(get_db)
):
    """Create a new tenant (public endpoint for tenant registration)"""
    try:
        tenant_service = TenantService(db)
        tenant = await tenant_service.create_tenant(
            name=tenant_data.name,
            contact_email=tenant_data.contact_email,
            contact_name=tenant_data.contact_name,
            subscription_tier=tenant_data.subscription_tier.value
        )
        
        return TenantResponse.model_validate(tenant)
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/tenant", response_model=TenantResponse)
async def get_current_tenant(
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current tenant information"""
    from app.models.database import Tenant
    
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    return TenantResponse.model_validate(tenant)

@router.put("/tenant", response_model=TenantResponse)
async def update_tenant(
    tenant_data: TenantUpdate,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(require_admin_role),
    db: Session = Depends(get_db)
):
    """Update tenant information (admin only)"""
    from app.models.database import Tenant
    
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Update tenant fields
    update_data = tenant_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tenant, field, value)
    
    db.commit()
    db.refresh(tenant)
    
    return TenantResponse.model_validate(tenant)

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
    
    return [UserResponse.model_validate(user) for user in users]

@router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return UserResponse.model_validate(current_user)

@router.put("/users/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    # Users can only update their own name, not role or active status
    allowed_fields = {"first_name", "last_name"}
    update_data = {k: v for k, v in user_data.model_dump(exclude_unset=True).items() if k in allowed_fields}
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)

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
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return UserResponse.model_validate(user)

# User Invitation Endpoints
@router.post("/invitations", response_model=InvitationResponse, status_code=201)
async def invite_user(
    invitation_data: UserInvite,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(require_admin_or_member_role),
    db: Session = Depends(get_db)
):
    """Invite a user to the tenant"""
    try:
        tenant_service = TenantService(db)
        invitation = await tenant_service.invite_user(
            tenant_id=tenant_id,
            email=invitation_data.email,
            role=invitation_data.role,
            invited_by_user_id=current_user.id
        )
        
        return InvitationResponse.model_validate(invitation)
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/invitations/accept", response_model=UserResponse, status_code=201)
async def accept_invitation(
    acceptance_data: UserInviteAccept,
    db: Session = Depends(get_db)
):
    """Accept user invitation and create account"""
    try:
        tenant_service = TenantService(db)
        user = await tenant_service.accept_invitation(
            token=acceptance_data.token,
            password=acceptance_data.password,
            first_name=acceptance_data.first_name,
            last_name=acceptance_data.last_name
        )
        
        return UserResponse.model_validate(user)
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/invitations", response_model=List[InvitationResponse])
async def get_invitations(
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(require_admin_or_member_role),
    db: Session = Depends(get_db)
):
    """Get all pending invitations for tenant"""
    from app.models.database import TenantInvitation, InvitationStatus
    
    invitations = db.query(TenantInvitation).filter(
        TenantInvitation.tenant_id == tenant_id,
        TenantInvitation.status == InvitationStatus.PENDING
    ).all()
    
    return [InvitationResponse.model_validate(invitation) for invitation in invitations]