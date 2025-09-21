from sqlalchemy import Column, String, DateTime, Integer, Text, JSON, Enum, Boolean, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid

# Import Base from the main database module to ensure consistency
from app.database import Base

class AgentStatus(str, enum.Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    TERMINATED = "terminated"

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Multi-tenant enums
class TenantStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    EXPIRED = "expired"
    PENDING = "pending"

class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"

class InvitationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

# Multi-tenant models
class Tenant(Base):
    __tablename__ = "tenants"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    subdomain = Column(String(100), unique=True, nullable=False)
    domain = Column(String(255), nullable=True)  # Custom domain
    status = Column(Enum(TenantStatus), default=TenantStatus.TRIAL)
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE)
    
    # Subscription details
    subscription_start = Column(DateTime(timezone=True))
    subscription_end = Column(DateTime(timezone=True))
    trial_end = Column(DateTime(timezone=True))
    
    # Usage limits
    max_agents = Column(Integer, default=5)
    max_tasks_per_month = Column(Integer, default=1000)
    max_storage_mb = Column(Integer, default=1000)
    max_users = Column(Integer, default=5)
    
    # Contact info
    contact_email = Column(String(255))
    contact_name = Column(String(255))
    
    # Metadata
    settings = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    invitations = relationship("TenantInvitation", back_populates="tenant", cascade="all, delete-orphan")
    agents = relationship("Agent", back_populates="tenant", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="tenant", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_subdomain', 'subdomain'),
        Index('idx_tenant_status', 'status'),
    )

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    role = Column(Enum(UserRole), default=UserRole.MEMBER)
    is_active = Column(Boolean, default=True)
    is_email_verified = Column(Boolean, default=False)
    
    # Multi-tenant
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    
    # Authentication
    last_login = Column(DateTime(timezone=True))
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True))
    
    # Metadata
    preferences = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint('email', 'tenant_id', name='uix_user_email_tenant'),
        Index('idx_user_email', 'email'),
        Index('idx_user_tenant', 'tenant_id'),
        Index('idx_user_active', 'is_active'),
    )

class TenantInvitation(Base):
    __tablename__ = "tenant_invitations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.MEMBER)
    status = Column(Enum(InvitationStatus), default=InvitationStatus.PENDING)
    token = Column(String(255), unique=True, nullable=False)
    
    # Multi-tenant
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    invited_by_user_id = Column(String, ForeignKey("users.id"))
    
    # Expiration
    expires_at = Column(DateTime(timezone=True), nullable=False)
    accepted_at = Column(DateTime(timezone=True))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant", back_populates="invitations")
    invited_by = relationship("User", foreign_keys=[invited_by_user_id])
    
    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint('email', 'tenant_id', name='uix_invitation_email_tenant'),
        Index('idx_invitation_token', 'token'),
        Index('idx_invitation_status', 'status'),
    )

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    action = Column(String(100), nullable=False)  # CREATE, UPDATE, DELETE, LOGIN, etc.
    resource_type = Column(String(100), nullable=False)  # Agent, Task, User, etc.
    resource_id = Column(String(255))
    
    # Multi-tenant
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"))
    
    # Details
    old_values = Column(JSON)
    new_values = Column(JSON)
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    
    # Metadata
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    tenant = relationship("Tenant", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_tenant_timestamp', 'tenant_id', 'timestamp'),
        Index('idx_audit_user', 'user_id'),
        Index('idx_audit_action', 'action'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
    )

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    agent_type = Column(String(100), nullable=False)  # gpt-4, claude, custom
    version = Column(String(50), default="1.0.0")
    status = Column(Enum(AgentStatus), default=AgentStatus.IDLE)
    configuration = Column(JSON)  # Agent-specific config
    capabilities = Column(JSON)  # List of capabilities
    resources = Column(JSON)  # CPU, memory, GPU requirements
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_active = Column(DateTime(timezone=True))
    
    # Multi-tenant
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="agents")
    tasks = relationship("Task", back_populates="agent")
    executions = relationship("TaskExecution", back_populates="agent")
    
    # Indexes
    __table_args__ = (
        Index('idx_agent_tenant', 'tenant_id'),
        Index('idx_agent_status', 'status'),
        Index('idx_agent_type', 'agent_type'),
    )

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    task_type = Column(String(100), nullable=False)  # text_processing, api_call, workflow
    input_data = Column(JSON)  # Task input parameters
    output_schema = Column(JSON)  # Expected output format
    priority = Column(Integer, default=1)  # 1=low, 5=high
    timeout_seconds = Column(Integer, default=300)
    retry_count = Column(Integer, default=3)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign Keys
    agent_id = Column(String, ForeignKey("agents.id"))
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    
    # Relationships
    agent = relationship("Agent", back_populates="tasks")
    tenant = relationship("Tenant")
    executions = relationship("TaskExecution", back_populates="task")
    
    # Indexes
    __table_args__ = (
        Index('idx_task_tenant', 'tenant_id'),
        Index('idx_task_agent', 'agent_id'),
        Index('idx_task_type', 'task_type'),
    )

class TaskExecution(Base):
    __tablename__ = "task_executions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    result = Column(JSON)  # Task execution result
    error_message = Column(Text)
    execution_time_ms = Column(Integer)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Foreign Keys
    agent_id = Column(String, ForeignKey("agents.id"))
    task_id = Column(String, ForeignKey("tasks.id"))
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    
    # Relationships
    agent = relationship("Agent", back_populates="executions")
    task = relationship("Task", back_populates="executions")
    tenant = relationship("Tenant")
    
    # Indexes
    __table_args__ = (
        Index('idx_execution_tenant', 'tenant_id'),
        Index('idx_execution_agent', 'agent_id'),
        Index('idx_execution_task', 'task_id'),
        Index('idx_execution_status', 'status'),
    )

class AgentMetrics(Base):
    __tablename__ = "agent_metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Performance metrics
    cpu_usage = Column(Integer)  # Percentage
    memory_usage = Column(Integer)  # MB
    tasks_completed = Column(Integer, default=0)
    tasks_failed = Column(Integer, default=0)
    average_response_time = Column(Integer)  # milliseconds
    
    # Business metrics
    success_rate = Column(Integer)  # Percentage
    throughput = Column(Integer)  # Tasks per hour
    cost = Column(Integer)  # Cost in cents
    
    # Relationships
    agent = relationship("Agent")
    tenant = relationship("Tenant")
    
    # Indexes
    __table_args__ = (
        Index('idx_metrics_tenant_timestamp', 'tenant_id', 'timestamp'),
        Index('idx_metrics_agent', 'agent_id'),
    )