"""
SQLAlchemy Database Models with Enterprise Multi-tenancy
Built for MVP simplicity, designed for billion-dollar platform scale.
"""

from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer, Float, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

Base = declarative_base()

# Enterprise Enums
class AgentStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class TaskType(str, enum.Enum):
    COMPLETION = "completion"
    ANALYSIS = "analysis"
    WORKFLOW = "workflow"
    INTEGRATION = "integration"
    CUSTOM = "custom"

class TenantStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"

class TenantTier(str, enum.Enum):
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class ComplianceLevel(str, enum.Enum):
    BASIC = "basic"
    ENTERPRISE = "enterprise"
    REGULATED = "regulated"

class SecurityClassification(str, enum.Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"


class TenantMixin:
    """
    Mixin for tenant isolation across all enterprise models.
    
    Current: Basic tenant_id field
    Future: Row-level security, tenant data encryption
    """
    tenant_id = Column(String(50), nullable=False, index=True)


class TimestampMixin:
    """Mixin for timestamp tracking"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

"""
SQLAlchemy Database Models with Enterprise Multi-tenancy
Built for MVP simplicity, designed for billion-dollar platform scale.
"""

from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer, Float, JSON, ForeignKey, Index, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

Base = declarative_base()

# Enterprise Enums
class AgentStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class TaskType(str, enum.Enum):
    COMPLETION = "completion"
    ANALYSIS = "analysis"
    WORKFLOW = "workflow"
    INTEGRATION = "integration"
    CUSTOM = "custom"

class TenantStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"

class TenantTier(str, enum.Enum):
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class ComplianceLevel(str, enum.Enum):
    BASIC = "basic"
    ENTERPRISE = "enterprise"
    REGULATED = "regulated"

class SecurityClassification(str, enum.Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"


class TenantMixin:
    """
    Mixin for tenant isolation across all enterprise models.
    
    Current: Basic tenant_id field
    Future: Row-level security, tenant data encryption
    """
    tenant_id = Column(String(50), nullable=False, index=True)


class TimestampMixin:
    """Mixin for timestamp tracking"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Agent(Base, TenantMixin, TimestampMixin):
    """
    Agent model with enterprise multi-tenancy.
    
    Current: Basic agent data with tenant isolation
    Future: Complex agent configurations, versioning, permissions
    """
    __tablename__ = "agents"
    
    # Primary key
    agent_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Agent metadata
    name = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(Enum(AgentStatus), default=AgentStatus.ACTIVE, nullable=False)
    
    # Agent configuration (stored as JSON for flexibility)
    config = Column(JSON, nullable=False)
    
    # Template reference
    template_id = Column(String(100), nullable=True)
    template_version = Column(String(20), nullable=True)
    
    # Enterprise features
    user_id = Column(String(100), nullable=False, index=True)
    approved_for_production = Column(Boolean, default=False)
    compliance_level = Column(Enum(ComplianceLevel), default=ComplianceLevel.BASIC)
    security_classification = Column(Enum(SecurityClassification), default=SecurityClassification.INTERNAL)
    
    # Performance tracking
    total_tasks = Column(Integer, default=0)
    successful_tasks = Column(Integer, default=0)
    failed_tasks = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    
    # Relationships
    tasks = relationship("Task", back_populates="agent", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="agent", cascade="all, delete-orphan")
    
    # Indexes for enterprise performance
    __table_args__ = (
        Index("ix_agents_tenant_status", "tenant_id", "status"),
        Index("ix_agents_tenant_user", "tenant_id", "user_id"),
        Index("ix_agents_template", "template_id"),
    )
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "agent_id": str(self.agent_id),
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "config": self.config,
            "template_id": self.template_id,
            "template_version": self.template_version,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "approved_for_production": self.approved_for_production,
            "compliance_level": self.compliance_level.value,
            "security_classification": self.security_classification.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "performance": {
                "total_tasks": self.total_tasks,
                "successful_tasks": self.successful_tasks,
                "failed_tasks": self.failed_tasks,
                "total_cost": self.total_cost
            }
        }


class Task(Base, TenantMixin, TimestampMixin):
    """
    Task execution model with enterprise tracking.
    
    Current: Basic task execution tracking
    Future: Complex workflow state, dependency tracking, SLA monitoring
    """
    __tablename__ = "tasks"
    
    # Primary key
    task_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Task definition
    task_type = Column(Enum(TaskType), nullable=False)
    priority = Column(Enum(TaskPriority), default=TaskPriority.NORMAL)
    
    # Task execution
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    input_data = Column(JSON, nullable=False)
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    timeout_seconds = Column(Integer, default=300)
    
    # Retry and error handling
    current_attempt = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    error_history = Column(JSON, default=list)
    
    # Enterprise tracking
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.agent_id"), nullable=False)
    user_id = Column(String(100), nullable=False, index=True)
    
    # Cost and usage tracking
    token_usage = Column(JSON, default=dict)  # {input_tokens, output_tokens, total_tokens}
    cost_estimate = Column(Float, default=0.0)
    provider = Column(String(50), nullable=True)  # openrouter, openai, anthropic
    model = Column(String(100), nullable=True)
    
    # Dependencies and workflow
    depends_on = Column(JSON, default=list)  # List of task IDs this task depends on
    callback_url = Column(String(500), nullable=True)
    
    # Execution metadata
    execution_node = Column(String(100), nullable=True)  # Which worker executed the task
    correlation_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    trace_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Relationships
    agent = relationship("Agent", back_populates="tasks")
    events = relationship("Event", back_populates="task", cascade="all, delete-orphan")
    
    # Indexes for enterprise performance
    __table_args__ = (
        Index("ix_tasks_tenant_status", "tenant_id", "status"),
        Index("ix_tasks_agent_status", "agent_id", "status"),
        Index("ix_tasks_user_status", "user_id", "status"),
        Index("ix_tasks_created_at", "created_at"),
        Index("ix_tasks_correlation", "correlation_id"),
    )
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "task_id": str(self.task_id),
            "task_type": self.task_type.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "input_data": self.input_data,
            "result": self.result,
            "error_message": self.error_message,
            "agent_id": str(self.agent_id),
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "execution_time_ms": self.execution_time_ms,
            "current_attempt": self.current_attempt,
            "max_retries": self.max_retries,
            "token_usage": self.token_usage,
            "cost_estimate": self.cost_estimate,
            "provider": self.provider,
            "model": self.model,
            "correlation_id": str(self.correlation_id) if self.correlation_id else None,
            "trace_id": str(self.trace_id) if self.trace_id else None
        }


class Template(Base, TimestampMixin):
    """
    Agent template model for enterprise template management.
    
    Current: Basic template storage
    Future: Template versioning, approval workflows, industry compliance
    """
    __tablename__ = "templates"
    
    # Primary key
    template_id = Column(String(100), primary_key=True)
    
    # Template metadata
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    version = Column(String(20), default="1.0.0", nullable=False)
    
    # Classification
    industry = Column(String(50), nullable=False)  # customer_service, sales, etc.
    category = Column(String(50), nullable=False)  # conversational, analytical, etc.
    
    # Template configuration
    config = Column(JSON, nullable=False)  # AgentConfig as JSON
    
    # Template features
    tags = Column(JSON, default=list)  # List of tags
    use_cases = Column(JSON, default=list)  # List of use cases
    requirements = Column(JSON, default=list)  # List of requirements
    
    # Enterprise governance
    compliance_level = Column(Enum(ComplianceLevel), default=ComplianceLevel.BASIC)
    security_classification = Column(Enum(SecurityClassification), default=SecurityClassification.PUBLIC)
    approved_for_production = Column(Boolean, default=False)
    
    # Template customization
    customizable_fields = Column(JSON, default=list)  # List of customizable fields
    required_integrations = Column(JSON, default=list)  # List of required integrations
    
    # Authorship and governance
    created_by = Column(String(100), nullable=False)
    approved_by = Column(String(100), nullable=True)
    approval_date = Column(DateTime, nullable=True)
    
    # Usage statistics
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    
    # Indexes
    __table_args__ = (
        Index("ix_templates_industry", "industry"),
        Index("ix_templates_category", "category"),
        Index("ix_templates_approved", "approved_for_production"),
    )
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "industry": self.industry,
            "category": self.category,
            "config": self.config,
            "tags": self.tags,
            "use_cases": self.use_cases,
            "requirements": self.requirements,
            "compliance_level": self.compliance_level.value,
            "security_classification": self.security_classification.value,
            "approved_for_production": self.approved_for_production,
            "customizable_fields": self.customizable_fields,
            "required_integrations": self.required_integrations,
            "created_by": self.created_by,
            "approved_by": self.approved_by,
            "approval_date": self.approval_date.isoformat() if self.approval_date else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "statistics": {
                "usage_count": self.usage_count,
                "success_rate": self.success_rate
            }
        }


class Event(Base, TenantMixin, TimestampMixin):
    """
    Event model for enterprise event sourcing and audit trails.
    
    Current: Basic event storage with tenant isolation
    Future: Event streaming, complex event processing, compliance archival
    """
    __tablename__ = "events"
    
    # Primary key
    event_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Event identification
    event_type = Column(String(100), nullable=False, index=True)
    version = Column(String(20), default="1.0", nullable=False)
    source = Column(String(100), default="agentcores", nullable=False)
    
    # Event payload
    data = Column(JSON, nullable=False)
    
    # Enterprise context
    user_id = Column(String(100), nullable=True, index=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.agent_id"), nullable=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.task_id"), nullable=True)
    
    # Tracing and correlation
    correlation_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    parent_event_id = Column(UUID(as_uuid=True), nullable=True)
    trace_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Event metadata
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    severity = Column(String(20), default="info")  # debug, info, warning, error, critical
    
    # Delivery tracking
    delivery_attempts = Column(Integer, default=0)
    last_delivery_attempt = Column(DateTime, nullable=True)
    delivered = Column(Boolean, default=False)
    
    # Retention and archival
    retention_policy = Column(String(50), default="standard")  # standard, extended, permanent
    archived = Column(Boolean, default=False)
    archived_at = Column(DateTime, nullable=True)
    
    # Relationships
    agent = relationship("Agent", back_populates="events")
    task = relationship("Task", back_populates="events")
    
    # Indexes for enterprise performance and compliance
    __table_args__ = (
        Index("ix_events_tenant_type", "tenant_id", "event_type"),
        Index("ix_events_tenant_created", "tenant_id", "created_at"),
        Index("ix_events_correlation", "correlation_id"),
        Index("ix_events_trace", "trace_id"),
        Index("ix_events_severity", "severity"),
        Index("ix_events_archived", "archived"),
    )
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "version": self.version,
            "source": self.source,
            "data": self.data,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "agent_id": str(self.agent_id) if self.agent_id else None,
            "task_id": str(self.task_id) if self.task_id else None,
            "correlation_id": str(self.correlation_id) if self.correlation_id else None,
            "parent_event_id": str(self.parent_event_id) if self.parent_event_id else None,
            "trace_id": str(self.trace_id) if self.trace_id else None,
            "priority": self.priority,
            "severity": self.severity,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "delivery_attempts": self.delivery_attempts,
            "last_delivery_attempt": self.last_delivery_attempt.isoformat() if self.last_delivery_attempt else None,
            "delivered": self.delivered,
            "retention_policy": self.retention_policy,
            "archived": self.archived,
            "archived_at": self.archived_at.isoformat() if self.archived_at else None
        }


class Tenant(Base, TimestampMixin):
    """
    Tenant model for enterprise multi-tenancy management.
    
    Current: Basic tenant metadata
    Future: Resource quotas, billing, compliance settings, data residency
    """
    __tablename__ = "tenants"
    
    # Primary key
    tenant_id = Column(String(50), primary_key=True)
    
    # Tenant metadata
    name = Column(String(100), nullable=False)
    description = Column(Text)
    domain = Column(String(100), nullable=True)  # Optional domain for tenant
    
    # Status and settings
    status = Column(Enum(TenantStatus), default=TenantStatus.ACTIVE)
    tier = Column(Enum(TenantTier), default=TenantTier.BASIC)
    
    # Enterprise features
    compliance_level = Column(Enum(ComplianceLevel), default=ComplianceLevel.BASIC)
    data_residency = Column(String(50), default="us-east-1")  # Data residency requirement
    
    # Resource quotas
    max_agents = Column(Integer, default=10)
    max_tasks_per_hour = Column(Integer, default=1000)
    max_monthly_cost = Column(Float, default=1000.0)
    
    # Usage tracking
    current_agents = Column(Integer, default=0)
    current_month_tasks = Column(Integer, default=0)
    current_month_cost = Column(Float, default=0.0)
    
    # Billing
    billing_email = Column(String(255), nullable=True)
    billing_plan = Column(String(50), default="pay_as_you_go")
    
    # Security settings
    ip_whitelist = Column(JSON, default=list)  # List of allowed IP addresses
    require_mfa = Column(Boolean, default=False)
    session_timeout_minutes = Column(Integer, default=480)  # 8 hours default
    
    # Indexes
    __table_args__ = (
        Index("ix_tenants_status", "status"),
        Index("ix_tenants_tier", "tier"),
        Index("ix_tenants_domain", "domain"),
    )
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "tenant_id": self.tenant_id,
            "name": self.name,
            "description": self.description,
            "domain": self.domain,
            "status": self.status.value,
            "tier": self.tier.value,
            "compliance_level": self.compliance_level.value,
            "data_residency": self.data_residency,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "quotas": {
                "max_agents": self.max_agents,
                "max_tasks_per_hour": self.max_tasks_per_hour,
                "max_monthly_cost": self.max_monthly_cost
            },
            "current_usage": {
                "agents": self.current_agents,
                "monthly_tasks": self.current_month_tasks,
                "monthly_cost": self.current_month_cost
            },
            "billing": {
                "email": self.billing_email,
                "plan": self.billing_plan
            },
            "security": {
                "ip_whitelist": self.ip_whitelist,
                "require_mfa": self.require_mfa,
                "session_timeout_minutes": self.session_timeout_minutes
            }
        }