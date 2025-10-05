"""
Modern Multi-Tenant FastAPI Application
Clean architecture without legacy system
"""

import hashlib
import json
import logging
import os
import secrets
import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt
from jose.exceptions import JWTError
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

# Import multi-tenant database functions
from app.database import get_individual_db, get_org_db
from app.models.database import Tenant, User, UserRole

# Configuration - Use environment variables for security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
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


def get_password_hash(password: str) -> str:
    """Simple password hashing with salt"""
    salt = secrets.token_bytes(32)
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return salt.hex() + ":" + pwd_hash.hex()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Simple password verification"""
    try:
        salt_hex, hash_hex = hashed_password.split(":")
        salt = bytes.fromhex(salt_hex)
        expected_hash = hashlib.pbkdf2_hmac(
            "sha256", plain_password.encode("utf-8"), salt, 100000
        )
        return expected_hash.hex() == hash_hex
    except Exception:
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
    version="2.0.0",
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
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/auth/register", response_model=LoginResponse)
async def register_user(registration: UserRegistrationRequest):
    """Register a new user with tenant creation and return login data"""
    db = None
    try:
        # Get appropriate database session
        db = get_appropriate_db(registration.is_individual_account)
        # Check both databases for duplicate email
        ind_db = next(get_individual_db())
        org_db = next(get_org_db())
        exists_in_ind = (
            ind_db.query(User).filter(User.email == registration.email).first()
        )
        exists_in_org = (
            org_db.query(User).filter(User.email == registration.email).first()
        )
        ind_db.close()
        org_db.close()
        if exists_in_ind or exists_in_org:
            db.close()
            raise HTTPException(
                status_code=400, detail="Email already registered in the system"
            )
        # Check if tenant already exists
        existing_tenant = (
            db.query(Tenant).filter(Tenant.name == registration.tenant_name).first()
        )
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
            tier="basic",
        )
        db.add(new_tenant)
        db.flush()  # Get the tenant ID
        # Create user with proper role assignment and validation
        user_role = (
            UserRole.INDIVIDUAL
            if registration.is_individual_account
            else UserRole.OWNER
        )
        hashed_password = get_password_hash(registration.password)
        db_type = "individual" if registration.is_individual_account else "organization"
        logger.info(
            f"Creating {user_role.value} user in {db_type} database for account type: {'individual' if registration.is_individual_account else 'organization'}"
        )
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
            last_login=datetime.utcnow(),  # Set initial login time
        )
        db.add(new_user)
        db.commit()
        logger.info(
            f"User registered successfully: {registration.email} in {'individual' if registration.is_individual_account else 'organization'} database"
        )

        # Extract user and tenant data while session is still open
        user_data = {
            "id": str(new_user.id),
            "email": new_user.email,
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "role": new_user.role.value,
            "tenant_id": new_user.tenant_id,
            "is_active": new_user.is_active,
        }

        tenant_data = {
            "id": new_tenant.id,
            "name": new_tenant.name,
            "status": new_tenant.status.value,
            "tier": new_tenant.tier.value,
        }

        db.close()

        # Create access token for automatic login
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": str(user_data["id"]),
                "email": user_data["email"],
                "tenant_id": str(user_data["tenant_id"]),
            },
            expires_delta=access_token_expires,
        )

        # Return login data format for seamless frontend integration
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_data,
            tenant=tenant_data,
        )

    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        if db is not None:
            try:
                db.rollback()
                db.close()
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")
    finally:
        if db is not None:
            try:
                db.close()
            except Exception:
                pass


@app.post("/auth/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """Authenticate user from appropriate database"""

    try:
        # Organization login logic
        if not login_data.is_individual_account:
            org_db = next(get_org_db())
            user = org_db.query(User).filter(User.email == login_data.email).first()
            if user:
                if not bool(user.is_active):
                    org_db.close()
                    raise HTTPException(status_code=401, detail="Account is inactive")
                if not verify_password(login_data.password, str(user.password_hash)):
                    org_db.close()
                    raise HTTPException(
                        status_code=401, detail="Incorrect email or password"
                    )
                # Only allow org roles
                org_roles = [
                    UserRole.OWNER,
                    UserRole.ADMIN,
                    UserRole.MANAGER,
                    UserRole.DEVELOPER,
                    UserRole.ANALYST,
                    UserRole.OPERATOR,
                    UserRole.VIEWER,
                    UserRole.GUEST,
                ]
                if user.role in org_roles:
                    tenant = (
                        org_db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
                    )
                    if not tenant:
                        org_db.close()
                        raise HTTPException(status_code=500, detail="Tenant not found")
                    setattr(user, "last_login", datetime.utcnow())
                    org_db.add(user)
                    org_db.commit()
                    user_data = {
                        "id": str(user.id),
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "role": user.role.value,
                        "tenant_id": user.tenant_id,
                        "is_active": user.is_active,
                    }
                    tenant_data = {
                        "id": tenant.id,
                        "name": tenant.name,
                        "status": tenant.status.value,
                        "tier": tenant.tier.value,
                    }
                    org_db.close()
                    access_token_expires = timedelta(
                        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
                    )
                    access_token = create_access_token(
                        data={
                            "sub": str(user_data["id"]),
                            "email": user_data["email"],
                            "tenant_id": str(user_data["tenant_id"]),
                        },
                        expires_delta=access_token_expires,
                    )
                    return LoginResponse(
                        access_token=access_token,
                        token_type="bearer",
                        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                        user=user_data,
                        tenant=tenant_data,
                    )
                else:
                    org_db.close()
                    # User is INDIVIDUAL in org DB
                    raise HTTPException(
                        status_code=401,
                        detail="This is an individual account. Please login as individual.",
                    )
            # Not found in org DB, check individual DB
            ind_db = next(get_individual_db())
            user = ind_db.query(User).filter(User.email == login_data.email).first()
            if user:
                ind_db.close()
                raise HTTPException(
                    status_code=401,
                    detail="This is an individual account. Please login as individual.",
                )
            ind_db.close()
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        # Individual login logic
        else:
            ind_db = next(get_individual_db())
            user = ind_db.query(User).filter(User.email == login_data.email).first()
            if user:
                if not bool(user.is_active):
                    ind_db.close()
                    raise HTTPException(status_code=401, detail="Account is inactive")
                if not verify_password(login_data.password, str(user.password_hash)):
                    ind_db.close()
                    raise HTTPException(
                        status_code=401, detail="Incorrect email or password"
                    )
                if getattr(user, "role", None) == UserRole.INDIVIDUAL:
                    tenant = (
                        ind_db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
                    )
                    if not tenant:
                        ind_db.close()
                        raise HTTPException(status_code=500, detail="Tenant not found")
                    setattr(user, "last_login", datetime.utcnow())
                    ind_db.add(user)
                    ind_db.commit()
                    user_data = {
                        "id": str(user.id),
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "role": user.role.value,
                        "tenant_id": user.tenant_id,
                        "is_active": user.is_active,
                    }
                    tenant_data = {
                        "id": tenant.id,
                        "name": tenant.name,
                        "status": tenant.status.value,
                        "tier": tenant.tier.value,
                    }
                    ind_db.close()
                    access_token_expires = timedelta(
                        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
                    )
                    access_token = create_access_token(
                        data={
                            "sub": str(user_data["id"]),
                            "email": user_data["email"],
                            "tenant_id": str(user_data["tenant_id"]),
                        },
                        expires_delta=access_token_expires,
                    )
                    return LoginResponse(
                        access_token=access_token,
                        token_type="bearer",
                        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                        user=user_data,
                        tenant=tenant_data,
                    )
                else:
                    ind_db.close()
                    raise HTTPException(
                        status_code=401,
                        detail="This is an organization account. Please login as organization.",
                    )
            # Not found in individual DB, check org DB
            org_db = next(get_org_db())
            user = org_db.query(User).filter(User.email == login_data.email).first()
            if user:
                org_db.close()
                raise HTTPException(
                    status_code=401,
                    detail="This is an organization account. Please login as organization.",
                )
            org_db.close()
            raise HTTPException(status_code=401, detail="Incorrect email or password")
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))


# Agent Models
class AgentCreateRequest(BaseModel):
    name: str
    description: str
    agent_type: str = "conversational"
    model: str = "openrouter/deepseek/deepseek-chat-v3.1:free"
    instructions: str = "You are a helpful AI assistant."
    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    memory_enabled: bool = True
    context_window: int = 4000
    max_memory_messages: int = 50
    response_style: str = "balanced"
    personality: str = "professional"
    safety_level: str = "standard"
    content_filter: bool = True
    response_timeout: int = 30
    rate_limit: int = 60


class AgentUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    agent_type: Optional[str] = None
    model: Optional[str] = None
    instructions: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    memory_enabled: Optional[bool] = None
    context_window: Optional[int] = None
    max_memory_messages: Optional[int] = None
    response_style: Optional[str] = None
    personality: Optional[str] = None
    safety_level: Optional[str] = None
    content_filter: Optional[bool] = None
    response_timeout: Optional[int] = None
    rate_limit: Optional[int] = None
    connected_agents: Optional[List[str]] = None


# Auth helper
async def get_current_user_from_token(token: str, db):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        tenant_id = payload.get("tenant_id")
        if not user_id or not tenant_id:
            return None
        user = (
            db.query(User)
            .filter(User.id == user_id, User.tenant_id == tenant_id)
            .first()
        )
        return user if user and user.is_active else None
    except Exception:
        return None


@app.post("/agents")
async def create_agent(agent_data: AgentCreateRequest, request: Request):
    """Create agent with tenant isolation"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Missing or invalid authorization header"
        )

    token = auth_header.split(" ")[1]

    # Determine database based on token payload
    db = None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        tenant_id = payload.get("tenant_id")
        email = payload.get("email")

        if not all([user_id, tenant_id, email]):
            raise HTTPException(status_code=401, detail="Invalid token payload")

        # Determine if individual or org account
        is_individual = False
        org_db = next(get_org_db())
        user = (
            org_db.query(User)
            .filter(User.id == user_id, User.tenant_id == tenant_id)
            .first()
        )
        if user:
            db = org_db
        else:
            org_db.close()
            ind_db = next(get_individual_db())
            user = (
                ind_db.query(User)
                .filter(User.id == user_id, User.tenant_id == tenant_id)
                .first()
            )
            if user:
                db = ind_db
                is_individual = True
            else:
                ind_db.close()
                raise HTTPException(status_code=401, detail="User not found")

        if not bool(user.is_active):
            db.close()
            raise HTTPException(status_code=401, detail="User account is inactive")

        # Create agent with tenant isolation (using actual DB schema)
        agent_id = str(uuid.uuid4())

        # Use raw SQL since the model doesn't match the actual schema
        from sqlalchemy import text

        insert_query = text(
            """
            INSERT INTO agents (id, tenant_id, name, description, template_id, provider, model, status, config, created_by)
            VALUES (:id, :tenant_id, :name, :description, :template_id, :provider, :model, :status, :config, :created_by)
            RETURNING id, name, description, status, config, created_at
        """
        )

        result = db.execute(
            insert_query,
            {
                "id": agent_id,
                "tenant_id": tenant_id,
                "name": agent_data.name,
                "description": agent_data.description,
                "template_id": "custom",
                "provider": "openrouter",
                "model": agent_data.model,
                "status": "active",
                "config": json.dumps(
                    {
                        "model": agent_data.model,
                        "instructions": agent_data.instructions,
                        "temperature": agent_data.temperature,
                        "max_tokens": agent_data.max_tokens,
                        "top_p": agent_data.top_p,
                        "frequency_penalty": agent_data.frequency_penalty,
                        "presence_penalty": agent_data.presence_penalty,
                        "agent_type": agent_data.agent_type,
                        "memory_enabled": agent_data.memory_enabled,
                        "context_window": agent_data.context_window,
                        "max_memory_messages": agent_data.max_memory_messages,
                        "response_style": agent_data.response_style,
                        "personality": agent_data.personality,
                        "safety_level": agent_data.safety_level,
                        "content_filter": agent_data.content_filter,
                        "response_timeout": agent_data.response_timeout,
                        "rate_limit": agent_data.rate_limit,
                    }
                ),
                "created_by": user.id,
            },
        )

        agent_row = result.fetchone()
        if not agent_row:
            db.close()
            raise HTTPException(
                status_code=500, detail="Failed to retrieve created agent"
            )

        db.commit()

        result = {
            "agent_id": str(agent_row[0]),
            "name": agent_row[1],
            "description": agent_row[2],
            "status": agent_row[3],
            "tenant_id": tenant_id,
            "user_id": str(user.id),
            "config": agent_row[4],
            "created_at": agent_row[5].isoformat(),
            "account_type": "individual" if is_individual else "organization",
        }

        db.close()
        logger.info(
            f"Agent created: {agent_id} for user {user_id} in tenant {tenant_id}"
        )
        return result

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        if db is not None:
            try:
                db.rollback()
                db.close()
            except Exception:
                pass
        logger.error(f"Agent creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Agent creation failed: {str(e)}")


@app.get("/agents")
async def get_agents(request: Request):
    """Get agents with tenant isolation"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Missing or invalid authorization header"
        )

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        tenant_id = payload.get("tenant_id")

        if not all([user_id, tenant_id]):
            raise HTTPException(status_code=401, detail="Invalid token payload")

        # Check both databases using raw SQL
        from sqlalchemy import text

        # Check org database
        org_db = next(get_org_db())
        org_query = text(
            "SELECT id, name, description, status, config, created_at, created_by FROM agents WHERE tenant_id = :tenant_id"
        )
        org_result = org_db.execute(org_query, {"tenant_id": tenant_id})
        org_agents = org_result.fetchall()
        org_db.close()

        # Check individual database
        ind_db = next(get_individual_db())
        ind_result = ind_db.execute(org_query, {"tenant_id": tenant_id})
        ind_agents = ind_result.fetchall()
        ind_db.close()

        all_agents = list(org_agents) + list(ind_agents)

        return {
            "agents": [
                {
                    "agent_id": str(agent[0]),
                    "name": agent[1],
                    "description": agent[2],
                    "status": agent[3],
                    "tenant_id": tenant_id,
                    "user_id": str(agent[5]) if agent[5] else None,
                    "config": agent[4],
                    "created_at": agent[5].isoformat() if agent[5] else None,
                }
                for agent in all_agents
            ],
            "total": len(all_agents),
            "tenant_id": tenant_id,
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Get agents failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Get agents failed: {str(e)}")


@app.post("/agents/{agent_id}/start")
async def start_agent(agent_id: str, request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        tenant_id = payload.get("tenant_id")
        if not tenant_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        from sqlalchemy import text

        update_query = text(
            "UPDATE agents SET status = 'running' WHERE id = :agent_id AND tenant_id = :tenant_id"
        )

        org_db = next(get_org_db())
        result = org_db.execute(
            update_query, {"agent_id": agent_id, "tenant_id": tenant_id}
        )
        if getattr(result, "rowcount", 1) > 0:
            org_db.commit()
            org_db.close()
            return {
                "message": "Agent started",
                "agent_id": agent_id,
                "status": "running",
            }
        org_db.close()

        ind_db = next(get_individual_db())
        result = ind_db.execute(
            update_query, {"agent_id": agent_id, "tenant_id": tenant_id}
        )
        if getattr(result, "rowcount", 1) > 0:
            ind_db.commit()
            ind_db.close()
            return {
                "message": "Agent started",
                "agent_id": agent_id,
                "status": "running",
            }
        ind_db.close()

        raise HTTPException(status_code=404, detail="Agent not found")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/agents/{agent_id}/stop")
async def stop_agent(agent_id: str, request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        tenant_id = payload.get("tenant_id")
        if not tenant_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        from sqlalchemy import text

        update_query = text(
            "UPDATE agents SET status = 'idle' WHERE id = :agent_id AND tenant_id = :tenant_id"
        )

        org_db = next(get_org_db())
        result = org_db.execute(
            update_query, {"agent_id": agent_id, "tenant_id": tenant_id}
        )
        try:
            row_affected = getattr(result, "rowcount", 1) > 0
        except (AttributeError, TypeError):
            row_affected = True  # Assume success if rowcount unavailable
        if row_affected:
            org_db.commit()
            org_db.close()
            return {"message": "Agent stopped", "agent_id": agent_id, "status": "idle"}
        org_db.close()

        ind_db = next(get_individual_db())
        result = ind_db.execute(
            update_query, {"agent_id": agent_id, "tenant_id": tenant_id}
        )
        if getattr(result, "rowcount", 1) > 0:
            ind_db.commit()
            ind_db.close()
            return {"message": "Agent stopped", "agent_id": agent_id, "status": "idle"}
        ind_db.close()

        raise HTTPException(status_code=404, detail="Agent not found")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.put("/agents/{agent_id}")
async def update_agent(
    agent_id: str, update_data: AgentUpdateRequest, request: Request
):
    """Update agent settings"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        tenant_id = payload.get("tenant_id")
        if not tenant_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        from sqlalchemy import text

        # Get current config and merge with updates
        get_query = text(
            "SELECT config FROM agents WHERE id = :agent_id AND tenant_id = :tenant_id"
        )
        update_query = text(
            """
            UPDATE agents
            SET name = COALESCE(:name, name),
                description = COALESCE(:description, description),
                config = :config
            WHERE id = :agent_id AND tenant_id = :tenant_id
            RETURNING id, name, description, status, config
        """
        )

        # Try org database first
        org_db = next(get_org_db())
        result = org_db.execute(
            get_query, {"agent_id": agent_id, "tenant_id": tenant_id}
        )
        current_row = result.fetchone()

        if current_row:
            # Handle config being either string or dict
            if current_row[0]:
                if isinstance(current_row[0], str):
                    current_config = json.loads(current_row[0])
                elif isinstance(current_row[0], dict):
                    current_config = current_row[0]
                else:
                    current_config = {}
            else:
                current_config = {}

            # Update config with new values
            if update_data.model:
                current_config["model"] = update_data.model
            if update_data.instructions:
                current_config["instructions"] = update_data.instructions
            if update_data.temperature is not None:
                current_config["temperature"] = update_data.temperature
            if update_data.max_tokens:
                current_config["max_tokens"] = update_data.max_tokens
            if update_data.top_p is not None:
                current_config["top_p"] = update_data.top_p
            if update_data.frequency_penalty is not None:
                current_config["frequency_penalty"] = update_data.frequency_penalty
            if update_data.presence_penalty is not None:
                current_config["presence_penalty"] = update_data.presence_penalty
            if update_data.memory_enabled is not None:
                current_config["memory_enabled"] = update_data.memory_enabled
            if update_data.context_window:
                current_config["context_window"] = update_data.context_window
            if update_data.max_memory_messages:
                current_config["max_memory_messages"] = update_data.max_memory_messages
            if update_data.response_style:
                current_config["response_style"] = update_data.response_style
            if update_data.personality:
                current_config["personality"] = update_data.personality
            if update_data.safety_level:
                current_config["safety_level"] = update_data.safety_level
            if update_data.content_filter is not None:
                current_config["content_filter"] = update_data.content_filter
            if update_data.response_timeout:
                current_config["response_timeout"] = update_data.response_timeout
            if update_data.rate_limit:
                current_config["rate_limit"] = update_data.rate_limit
            if update_data.agent_type:
                current_config["agent_type"] = update_data.agent_type
            if update_data.connected_agents is not None:
                current_config["connected_agents"] = update_data.connected_agents

            result = org_db.execute(
                update_query,
                {
                    "agent_id": agent_id,
                    "tenant_id": tenant_id,
                    "name": update_data.name,
                    "description": update_data.description,
                    "config": json.dumps(current_config),
                },
            )

            if getattr(result, "rowcount", 1) > 0:
                agent_row = result.fetchone()
                if not agent_row:
                    org_db.close()
                    raise HTTPException(
                        status_code=404, detail="Agent not found after update"
                    )
                org_db.commit()
                org_db.close()
                return {
                    "agent_id": str(agent_row[0]),
                    "name": agent_row[1],
                    "description": agent_row[2],
                    "status": agent_row[3],
                    "config": agent_row[4],
                    "message": "Agent updated successfully",
                }
        org_db.close()

        # Try individual database
        ind_db = next(get_individual_db())
        result = ind_db.execute(
            get_query, {"agent_id": agent_id, "tenant_id": tenant_id}
        )
        current_row = result.fetchone()

        if current_row:
            # Handle config being either string or dict
            if current_row[0]:
                if isinstance(current_row[0], str):
                    current_config = json.loads(current_row[0])
                elif isinstance(current_row[0], dict):
                    current_config = current_row[0]
                else:
                    current_config = {}
            else:
                current_config = {}

            # Update config with new values
            if update_data.model:
                current_config["model"] = update_data.model
            if update_data.instructions:
                current_config["instructions"] = update_data.instructions
            if update_data.temperature is not None:
                current_config["temperature"] = update_data.temperature
            if update_data.max_tokens:
                current_config["max_tokens"] = update_data.max_tokens
            if update_data.top_p is not None:
                current_config["top_p"] = update_data.top_p
            if update_data.frequency_penalty is not None:
                current_config["frequency_penalty"] = update_data.frequency_penalty
            if update_data.presence_penalty is not None:
                current_config["presence_penalty"] = update_data.presence_penalty
            if update_data.memory_enabled is not None:
                current_config["memory_enabled"] = update_data.memory_enabled
            if update_data.context_window:
                current_config["context_window"] = update_data.context_window
            if update_data.max_memory_messages:
                current_config["max_memory_messages"] = update_data.max_memory_messages
            if update_data.response_style:
                current_config["response_style"] = update_data.response_style
            if update_data.personality:
                current_config["personality"] = update_data.personality
            if update_data.safety_level:
                current_config["safety_level"] = update_data.safety_level
            if update_data.content_filter is not None:
                current_config["content_filter"] = update_data.content_filter
            if update_data.response_timeout:
                current_config["response_timeout"] = update_data.response_timeout
            if update_data.rate_limit:
                current_config["rate_limit"] = update_data.rate_limit
            if update_data.agent_type:
                current_config["agent_type"] = update_data.agent_type
            if update_data.connected_agents is not None:
                current_config["connected_agents"] = update_data.connected_agents

            result = ind_db.execute(
                update_query,
                {
                    "agent_id": agent_id,
                    "tenant_id": tenant_id,
                    "name": update_data.name,
                    "description": update_data.description,
                    "config": json.dumps(current_config),
                },
            )

            if getattr(result, "rowcount", 1) > 0:
                agent_row = result.fetchone()
                if not agent_row:
                    ind_db.close()
                    raise HTTPException(
                        status_code=404, detail="Agent not found after update"
                    )
                ind_db.commit()
                ind_db.close()
                return {
                    "agent_id": str(agent_row[0]),
                    "name": agent_row[1],
                    "description": agent_row[2],
                    "status": agent_row[3],
                    "config": agent_row[4],
                    "message": "Agent updated successfully",
                }
        ind_db.close()

        raise HTTPException(status_code=404, detail="Agent not found")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Agent update failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Agent update failed: {str(e)}")


@app.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str, request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        tenant_id = payload.get("tenant_id")
        if not tenant_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        from sqlalchemy import text

        delete_query = text(
            "DELETE FROM agents WHERE id = :agent_id AND tenant_id = :tenant_id"
        )

        org_db = next(get_org_db())
        result = org_db.execute(
            delete_query, {"agent_id": agent_id, "tenant_id": tenant_id}
        )
        if getattr(result, "rowcount", 1) > 0:
            org_db.commit()
            org_db.close()
            return {"message": "Agent deleted", "agent_id": agent_id}
        org_db.close()

        ind_db = next(get_individual_db())
        result = ind_db.execute(
            delete_query, {"agent_id": agent_id, "tenant_id": tenant_id}
        )
        if getattr(result, "rowcount", 1) > 0:
            ind_db.commit()
            ind_db.close()
            return {"message": "Agent deleted", "agent_id": agent_id}
        ind_db.close()

        raise HTTPException(status_code=404, detail="Agent not found")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Chat endpoints
class ChatRequest(BaseModel):
    message: str
    agent_id: str


@app.post("/agents/{agent_id}/chat")
async def chat_with_agent(agent_id: str, chat_request: ChatRequest, request: Request):
    """Chat with an agent"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        tenant_id = payload.get("tenant_id")
        if not all([user_id, tenant_id]):
            raise HTTPException(status_code=401, detail="Invalid token")

        # Get agent from database
        from sqlalchemy import text

        agent_query = text(
            "SELECT id, name, config FROM agents WHERE id = :agent_id AND tenant_id = :tenant_id"
        )

        agent = None
        org_db = next(get_org_db())
        result = org_db.execute(
            agent_query, {"agent_id": agent_id, "tenant_id": tenant_id}
        )
        agent_row = result.fetchone()
        if agent_row:
            agent = agent_row
        org_db.close()

        if not agent:
            ind_db = next(get_individual_db())
            result = ind_db.execute(
                agent_query, {"agent_id": agent_id, "tenant_id": tenant_id}
            )
            agent_row = result.fetchone()
            if agent_row:
                agent = agent_row
            ind_db.close()

        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        # Get agent response using OpenRouter
        import os

        import httpx

        config = json.loads(agent[2]) if isinstance(agent[2], str) else agent[2]
        model = config.get("model", "openrouter/deepseek/deepseek-chat-v3.1:free")

        # Ensure we have openrouter/ prefix for consistency
        if not model.startswith("openrouter/"):
            model = f"openrouter/{model}"

        # Map legacy models to verified working free models on OpenRouter
        model_mappings = {
            # Legacy Meta Llama models -> Newer versions
            "openrouter/meta-llama/llama-3.2-3b-instruct:free": "openrouter/meta-llama/llama-3.3-8b-instruct:free",
            "openrouter/meta-llama/llama-3.2-1b-instruct:free": "openrouter/meta-llama/llama-3.3-8b-instruct:free",
            "openrouter/meta-llama/llama-3.1-8b-instruct:free": "openrouter/meta-llama/llama-3.3-8b-instruct:free",
            "openrouter/meta-llama/llama-3.1-70b-instruct:free": "openrouter/meta-llama/llama-3.3-70b-instruct:free",
            "openrouter/meta-llama/llama-3.1-405b-instruct:free": "openrouter/meta-llama/llama-4-maverick:free",
            # Legacy Mistral models -> Working versions
            "openrouter/mistralai/mistral-7b-instruct:free": "openrouter/mistralai/mistral-nemo:free",
            # Legacy Google models -> Working Gemma models
            "openrouter/google/gemma-7b-it:free": "openrouter/google/gemma-3-12b-it:free",
            "openrouter/google/gemma-2-9b-it:free": "openrouter/google/gemma-3-12b-it:free",
            "openrouter/google/gemini-2.0-flash-exp:free": "openrouter/google/gemma-3-27b-it:free",
            # Other legacy models -> NVIDIA Nemotron
            "openrouter/microsoft/phi-3-mini-128k-instruct:free": "openrouter/nvidia/nemotron-nano-9b-v2:free",
            "openrouter/openai/gpt-oss-20b:free": "openrouter/nvidia/nemotron-nano-9b-v2:free",
            # Non-functional models -> Working alternatives
            "openrouter/x-ai/grok-4-fast:free": "openrouter/deepseek/deepseek-chat-v3.1:free",
            "openrouter/qwen/qwen3-coder:free": "openrouter/qwen/qwen-2.5-72b-instruct:free",
            "openrouter/deepseek/deepseek-r1:free": "openrouter/deepseek/deepseek-chat-v3.1:free",
        }

        if model in model_mappings:
            model = model_mappings[model]

        # Remove openrouter/ prefix for API call (OpenRouter expects just the model name)
        api_model = model[11:] if model.startswith("openrouter/") else model

        instructions = config.get("instructions", "You are a helpful AI assistant.")
        temperature = max(0.0, min(2.0, float(config.get("temperature", 0.7))))
        max_tokens = max(1, min(8000, int(config.get("max_tokens", 1000))))
        top_p = max(0.0, min(1.0, float(config.get("top_p", 1.0))))
        frequency_penalty = max(
            -2.0, min(2.0, float(config.get("frequency_penalty", 0.0)))
        )
        presence_penalty = max(
            -2.0, min(2.0, float(config.get("presence_penalty", 0.0)))
        )

        # Apply personality and response style to instructions
        personality = config.get("personality", "professional")
        response_style = config.get("response_style", "balanced")
        safety_level = config.get("safety_level", "standard")
        blocked_topics = config.get("blocked_topics", "")
        content_filter = config.get("content_filter", True)

        # Enhanced instructions based on settings with security controls
        enhanced_instructions = instructions

        # Security controls - always apply regardless of settings
        enhanced_instructions += " SECURITY: Never provide harmful, illegal, or dangerous content. Do not assist with illegal activities, violence, or harmful actions."

        # Apply safety level controls
        if safety_level == "strict":
            enhanced_instructions += " STRICT MODE: Be extremely cautious about any potentially sensitive content. Refuse requests that could be harmful in any way."
        elif safety_level == "permissive":
            enhanced_instructions += " PERMISSIVE MODE: You can discuss sensitive topics but still maintain ethical boundaries."

        # Apply content filtering
        if content_filter:
            enhanced_instructions += " Apply content filtering to avoid inappropriate, offensive, or harmful content."

        # Apply blocked topics
        if blocked_topics:
            topics_list = [
                topic.strip() for topic in blocked_topics.split(",") if topic.strip()
            ]
            if topics_list:
                enhanced_instructions += f" BLOCKED TOPICS: Refuse to discuss or provide information about: {', '.join(topics_list)}."

        # Apply personality
        if personality != "professional":
            enhanced_instructions += (
                f" Adopt a {personality} personality in your responses."
            )

        # Apply response style
        if response_style == "concise":
            enhanced_instructions += " Keep responses brief and to the point."
        elif response_style == "detailed":
            enhanced_instructions += " Provide detailed, comprehensive responses."
        elif response_style == "step_by_step":
            enhanced_instructions += (
                " Break down complex topics into step-by-step explanations."
            )

        # Check if API key is properly configured
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key or api_key == "sk-or-v1-your-key-here":
            return {
                "message": {
                    "id": str(uuid.uuid4()),
                    "agent_id": agent_id,
                    "message": chat_request.message,
                    "sender": "user",
                    "timestamp": datetime.utcnow().isoformat(),
                },
                "response": {
                    "id": str(uuid.uuid4()),
                    "agent_id": agent_id,
                    "message": "Chat functionality is not available. Please configure the OPENROUTER_API_KEY environment variable.",
                    "sender": "agent",
                    "timestamp": datetime.utcnow().isoformat(),
                },
            }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "AgentCores",
        }

        # Build messages with enhanced instructions
        messages = [{"role": "system", "content": enhanced_instructions}]
        messages.append({"role": "user", "content": chat_request.message})

        payload = {
            "model": api_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
            )

            if response.status_code != 200:
                try:
                    error_detail = response.json()
                    logger.error(
                        f"OpenRouter API Error {response.status_code}: {error_detail}"
                    )
                    agent_response = f"I apologize, but I encountered an error: {response.status_code}. Please check the API configuration."
                except Exception:
                    logger.error(
                        f"OpenRouter API Error {response.status_code}: {response.text}"
                    )
                    agent_response = f"I apologize, but I encountered an error: {response.status_code}. Please check the API configuration."
            else:
                result = response.json()
                agent_response = result["choices"][0]["message"]["content"]

        return {
            "message": {
                "id": str(uuid.uuid4()),
                "agent_id": agent_id,
                "message": chat_request.message,
                "sender": "user",
                "timestamp": datetime.utcnow().isoformat(),
            },
            "response": {
                "id": str(uuid.uuid4()),
                "agent_id": agent_id,
                "message": agent_response,
                "sender": "agent",
                "timestamp": datetime.utcnow().isoformat(),
            },
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error("Chat failed: %s", str(e))
        return {
            "message": {
                "id": str(uuid.uuid4()),
                "agent_id": agent_id,
                "message": chat_request.message,
                "sender": "user",
                "timestamp": datetime.utcnow().isoformat(),
            },
            "response": {
                "id": str(uuid.uuid4()),
                "agent_id": agent_id,
                "message": f"I apologize, but I encountered an error: {str(e)}",
                "sender": "agent",
                "timestamp": datetime.utcnow().isoformat(),
            },
        }


@app.get("/agents/{agent_id}/chat/history")
async def get_chat_history(agent_id: str, request: Request):
    """Get chat history (placeholder - returns empty for now)"""
    return {"messages": []}


@app.get("/agents/available/{agent_id}")
async def get_available_agents_for_connection(agent_id: str, request: Request):
    """Get available agents for connection"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        tenant_id = payload.get("tenant_id")
        if not tenant_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        from sqlalchemy import text

        query = text(
            "SELECT id, name, description, status FROM agents WHERE tenant_id = :tenant_id AND id != :agent_id"
        )

        # Check org database
        org_db = next(get_org_db())
        result = org_db.execute(query, {"tenant_id": tenant_id, "agent_id": agent_id})
        org_agents = result.fetchall()
        org_db.close()

        # Check individual database
        ind_db = next(get_individual_db())
        result = ind_db.execute(query, {"tenant_id": tenant_id, "agent_id": agent_id})
        ind_agents = result.fetchall()
        ind_db.close()

        all_agents = list(org_agents) + list(ind_agents)

        return {
            "agents": [
                {
                    "id": str(agent[0]),
                    "name": agent[1],
                    "description": agent[2],
                    "status": agent[3],
                }
                for agent in all_agents
            ]
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
