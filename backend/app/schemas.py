from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    TERMINATED = "terminated"

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Multi-tenant enums
class TenantStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    EXPIRED = "expired"
    PENDING = "pending"

class SubscriptionTier(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class UserRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"

# Agent Schemas
class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    agent_type: str = Field(..., description="Type of agent (gpt-4, claude, custom)")
    model: str = Field(default="openrouter/anthropic/claude-3-haiku")
    instructions: Optional[str] = Field(default="You are a helpful AI assistant.")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, ge=1, le=8000)
    version: str = Field(default="1.0.0")
    configuration: Optional[Dict[str, Any]] = Field(default_factory=dict)
    capabilities: Optional[List[str]] = Field(default_factory=list)
    resources: Optional[Dict[str, Any]] = Field(default_factory=dict)
    connected_agents: Optional[List[str]] = Field(default_factory=list)

class AgentCreate(AgentBase):
    pass

class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[AgentStatus] = None
    configuration: Optional[Dict[str, Any]] = None
    capabilities: Optional[List[str]] = None
    resources: Optional[Dict[str, Any]] = None

class Agent(AgentBase):
    id: str
    status: AgentStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_active: Optional[datetime] = None
    created_by: Optional[str] = None

    class Config:
        from_attributes = True

# Task Schemas
class TaskBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    task_type: str = Field(..., description="Type of task (text_processing, api_call, workflow)")
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Optional[Dict[str, Any]] = None
    priority: int = Field(default=1, ge=1, le=5)
    timeout_seconds: int = Field(default=300, ge=1, le=3600)
    retry_count: int = Field(default=3, ge=0, le=10)

class TaskCreate(TaskBase):
    agent_id: str

class TaskUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    timeout_seconds: Optional[int] = Field(None, ge=1, le=3600)

class Task(TaskBase):
    id: str
    agent_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Task Execution Schemas
class TaskExecutionBase(BaseModel):
    status: TaskStatus
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None

class TaskExecutionCreate(TaskExecutionBase):
    agent_id: str
    task_id: str

class TaskExecution(TaskExecutionBase):
    id: str
    agent_id: str
    task_id: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Chat Schemas
class ChatMessage(BaseModel):
    id: str
    agent_id: str
    message: str
    sender: str  # 'user' or 'agent'
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    agent_id: str

class ChatResponse(BaseModel):
    message: ChatMessage
    response: ChatMessage

# Response Schemas
class AgentListResponse(BaseModel):
    agents: List[Agent]
    total: int
    page: int
    size: int

class TaskListResponse(BaseModel):
    tasks: List[Task]
    total: int
    page: int
    size: int

class TaskExecutionResponse(BaseModel):
    execution: TaskExecution
    task: Task
    agent: Agent

# Health Check
class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0"

# Authentication Schemas
class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    tenant_name: str = Field(..., min_length=1, description="Organization name")

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    tenant_name: str = Field(..., min_length=1, description="Organization name")

class UserInviteAccept(BaseModel):
    token: str
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole

class UserResponse(UserBase):
    id: str
    tenant_id: str
    is_active: bool
    is_email_verified: bool
    last_login: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserInvite(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.MEMBER

# Tenant Schemas
class TenantCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    contact_email: EmailStr
    contact_name: str = Field(..., min_length=1, max_length=255)
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE

class TenantResponse(BaseModel):
    id: str
    name: str
    status: TenantStatus
    subscription_tier: SubscriptionTier
    max_agents: int
    max_tasks_per_month: int
    max_storage_mb: int
    max_users: int
    trial_end: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TenantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    contact_email: Optional[EmailStr] = None
    contact_name: Optional[str] = Field(None, min_length=1, max_length=255)
    settings: Optional[Dict[str, Any]] = None

# Invitation Schemas
class InvitationResponse(BaseModel):
    id: str
    email: EmailStr
    role: UserRole
    status: str
    expires_at: datetime
    created_at: datetime
    invited_by: Optional[UserResponse] = None

    class Config:
        from_attributes = True

# Token Response - Defined after UserResponse and TenantResponse to avoid forward reference issues
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
    tenant: TenantResponse