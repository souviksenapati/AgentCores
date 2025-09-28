"""
Modern Multi-Tenant FastAPI Application
Clean architecture without legacy system
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pydantic import BaseModel, EmailStr
import logging
from passlib.context import CryptContext
from jose import JWTError, jwt

# Import multi-tenant database functions
from app.database import get_individual_db, get_org_db, get_db_session
from app.models.database import User, Tenant, UserRole

# Configuration
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic Models
class UserRegistrationRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    tenant_name: str
    is_individual_account: bool = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    is_individual_account: bool = True

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict
    tenant: dict

# Helper Functions
# Simple password hashing functions (inline)
import hashlib
import secrets

def get_password_hash(password: str) -> str:
    """Simple password hashing with salt"""
    salt = secrets.token_bytes(32)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + ':' + pwd_hash.hex()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Simple password verification"""
    try:
        salt_hex, hash_hex = hashed_password.split(':')
        salt = bytes.fromhex(salt_hex)
        expected_hash = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, 100000)
        return expected_hash.hex() == hash_hex
    except:
        return False

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

def get_appropriate_db(is_individual: bool):
    """Get the appropriate database session based on user type"""
    if is_individual:
        return next(get_individual_db())
    else:
        return next(get_org_db())

# FastAPI App
app = FastAPI(
    title="AgentCores Multi-Tenant API",
    description="Modern multi-tenant AI agent platform",
    version="2.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "AgentCores Multi-Tenant API",
        "version": "2.0.0",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/auth/register", response_model=LoginResponse)
async def register_user(registration: UserRegistrationRequest):
    """Register a new user with tenant creation and return login data"""
    try:
        # Get appropriate database session
        db = get_appropriate_db(registration.is_individual_account)
        # Check both databases for duplicate email
        ind_db = next(get_individual_db())
        org_db = next(get_org_db())
        exists_in_ind = ind_db.query(User).filter(User.email == registration.email).first()
        exists_in_org = org_db.query(User).filter(User.email == registration.email).first()
        ind_db.close()
        org_db.close()
        if exists_in_ind or exists_in_org:
            db.close()
            raise HTTPException(status_code=400, detail="Email already registered in the system")
        # Check if tenant already exists
        existing_tenant = db.query(Tenant).filter(Tenant.name == registration.tenant_name).first()
        if existing_tenant:
            db.close()
            raise HTTPException(status_code=400, detail="Tenant name already exists")
        # Create tenant
        tenant_id = str(uuid.uuid4())
        new_tenant = Tenant(
            id=tenant_id,
            name=registration.tenant_name,
            description=f"Tenant for {registration.tenant_name}",
            status="active",
            tier="basic"
        )
        db.add(new_tenant)
        db.flush()  # Get the tenant ID
        # Create user with proper role assignment and validation
        user_role = UserRole.INDIVIDUAL if registration.is_individual_account else UserRole.OWNER
        hashed_password = get_password_hash(registration.password)
        db_type = "individual" if registration.is_individual_account else "organization"
        logger.info(f"Creating {user_role.value} user in {db_type} database for account type: {'individual' if registration.is_individual_account else 'organization'}")
        new_user = User(
            id=uuid.uuid4(),
            email=registration.email,
            first_name=registration.first_name,
            last_name=registration.last_name,
            password_hash=hashed_password,
            tenant_id=tenant_id,
            role=user_role,
            is_active=True,
            is_verified=True,
            last_login=datetime.utcnow()  # Set initial login time
        )
        db.add(new_user)
        db.commit()
        logger.info(f"User registered successfully: {registration.email} in {'individual' if registration.is_individual_account else 'organization'} database")
        
        # Extract user and tenant data while session is still open
        user_data = {
            "id": str(new_user.id),
            "email": new_user.email,
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "role": new_user.role.value,
            "tenant_id": new_user.tenant_id,
            "is_active": new_user.is_active
        }
        
        tenant_data = {
            "id": new_tenant.id,
            "name": new_tenant.name,
            "status": new_tenant.status.value,
            "tier": new_tenant.tier.value
        }
        
        db.close()
        
        # Create access token for automatic login
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user_data["id"]), "email": user_data["email"], "tenant_id": str(user_data["tenant_id"])},
            expires_delta=access_token_expires
        )
        
        # Return login data format for seamless frontend integration
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_data,
            tenant=tenant_data
        )
        
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        if 'db' in locals():
            db.rollback()
            db.close()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")
    finally:
        if 'db' in locals():
            db.close()

@app.post("/auth/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """Authenticate user from appropriate database"""
    
    try:
        # Organization login logic
        if not login_data.is_individual_account:
            org_db = next(get_org_db())
            user = org_db.query(User).filter(User.email == login_data.email).first()
            if user:
                if not user.is_active:
                    org_db.close()
                    raise HTTPException(status_code=401, detail="Account is inactive")
                if not verify_password(login_data.password, user.password_hash):
                    org_db.close()
                    raise HTTPException(status_code=401, detail="Incorrect email or password")
                # Only allow org roles
                org_roles = [UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.DEVELOPER, UserRole.ANALYST, UserRole.OPERATOR, UserRole.VIEWER, UserRole.GUEST]
                if user.role in org_roles:
                    tenant = org_db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
                    user.last_login = datetime.utcnow()
                    org_db.add(user)
                    org_db.commit()
                    user_data = {
                        "id": str(user.id),
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "role": user.role.value,
                        "tenant_id": user.tenant_id,
                        "is_active": user.is_active
                    }
                    tenant_data = {
                        "id": tenant.id,
                        "name": tenant.name,
                        "status": tenant.status.value,
                        "tier": tenant.tier.value
                    }
                    org_db.close()
                    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                    access_token = create_access_token(
                        data={"sub": str(user_data["id"]), "email": user_data["email"], "tenant_id": str(user_data["tenant_id"])} ,
                        expires_delta=access_token_expires
                    )
                    return LoginResponse(
                        access_token=access_token,
                        token_type="bearer",
                        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                        user=user_data,
                        tenant=tenant_data
                    )
                else:
                    org_db.close()
                    # User is INDIVIDUAL in org DB
                    raise HTTPException(status_code=401, detail="This is an individual account. Please login as individual.")
            # Not found in org DB, check individual DB
            ind_db = next(get_individual_db())
            user = ind_db.query(User).filter(User.email == login_data.email).first()
            if user:
                ind_db.close()
                raise HTTPException(status_code=401, detail="This is an individual account. Please login as individual.")
            ind_db.close()
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        # Individual login logic
        else:
            ind_db = next(get_individual_db())
            user = ind_db.query(User).filter(User.email == login_data.email).first()
            if user:
                if not user.is_active:
                    ind_db.close()
                    raise HTTPException(status_code=401, detail="Account is inactive")
                if not verify_password(login_data.password, user.password_hash):
                    ind_db.close()
                    raise HTTPException(status_code=401, detail="Incorrect email or password")
                if user.role == UserRole.INDIVIDUAL:
                    tenant = ind_db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
                    user.last_login = datetime.utcnow()
                    ind_db.add(user)
                    ind_db.commit()
                    user_data = {
                        "id": str(user.id),
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "role": user.role.value,
                        "tenant_id": user.tenant_id,
                        "is_active": user.is_active
                    }
                    tenant_data = {
                        "id": tenant.id,
                        "name": tenant.name,
                        "status": tenant.status.value,
                        "tier": tenant.tier.value
                    }
                    ind_db.close()
                    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                    access_token = create_access_token(
                        data={"sub": str(user_data["id"]), "email": user_data["email"], "tenant_id": str(user_data["tenant_id"])} ,
                        expires_delta=access_token_expires
                    )
                    return LoginResponse(
                        access_token=access_token,
                        token_type="bearer",
                        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                        user=user_data,
                        tenant=tenant_data
                    )
                else:
                    ind_db.close()
                    raise HTTPException(status_code=401, detail="This is an organization account. Please login as organization.")
            # Not found in individual DB, check org DB
            org_db = next(get_org_db())
            user = org_db.query(User).filter(User.email == login_data.email).first()
            if user:
                org_db.close()
                raise HTTPException(status_code=401, detail="This is an organization account. Please login as organization.")
            org_db.close()
            raise HTTPException(status_code=401, detail="Incorrect email or password")
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)