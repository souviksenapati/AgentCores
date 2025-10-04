"""
Core interfaces and abstractions for enterprise-scale agent management.
These interfaces will support the future Neural Orchestration Layer.
"""

import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel


class AgentType(str, Enum):
    """Agent types that will expand to support industry-specific agents"""

    CHATBOT = "chatbot"
    CONTENT_GENERATOR = "content_generator"
    DATA_PROCESSOR = "data_processor"
    # Future enterprise types:
    # FINANCIAL_ANALYST = "financial_analyst"
    # HEALTHCARE_ASSISTANT = "healthcare_assistant"
    # MANUFACTURING_OPTIMIZER = "manufacturing_optimizer"


class AgentStatus(str, Enum):
    """Agent lifecycle states for enterprise workflow management"""

    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    TRAINING = "training"
    DEPLOYED = "deployed"
    RETIRED = "retired"


class TaskStatus(str, Enum):
    """Task execution states for workflow orchestration"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class ProviderType(str, Enum):
    """AI Provider types - expandable for multi-cloud AI"""

    OPENROUTER = "openrouter"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure_openai"
    AWS_BEDROCK = "aws_bedrock"
    GOOGLE_VERTEX = "google_vertex"
    CUSTOM = "custom"


# Core Data Models with Enterprise DNA
class AgentConfig(BaseModel):
    """Agent configuration that scales to complex enterprise scenarios"""

    name: str
    description: str
    agent_type: AgentType
    provider: ProviderType
    model: str
    system_prompt: str
    temperature: float = 0.7
    max_tokens: int = 1000

    # Enterprise features (simple now, complex later)
    tags: List[str] = []
    compliance_tags: List[str] = []  # Future: GDPR, HIPAA, SOX
    resource_limits: Dict[str, Any] = {}  # Future: CPU, Memory, GPU
    sla_requirements: Dict[str, Any] = {}  # Future: Latency, Availability


class TaskRequest(BaseModel):
    """Task request that supports future workflow orchestration"""

    agent_id: str
    input_data: Union[str, Dict[str, Any]]
    task_type: str = "completion"

    # Enterprise workflow features
    priority: int = 5  # 1-10 scale for future resource scheduling
    timeout_seconds: int = 300
    retry_policy: Dict[str, Any] = {"max_retries": 3, "backoff": "exponential"}
    context: Dict[str, Any] = {}  # Future: Workflow context, dependencies


class TaskResult(BaseModel):
    """Task result with enterprise monitoring data"""

    task_id: str
    status: TaskStatus
    result: Optional[Union[str, Dict[str, Any]]] = None
    error_message: Optional[str] = None

    # Enterprise analytics
    started_at: datetime
    completed_at: Optional[datetime] = None
    execution_time_ms: Optional[int] = None
    token_usage: Dict[str, int] = {}  # input_tokens, output_tokens
    cost_estimate: Optional[float] = None


# Core Interfaces for Enterprise Architecture
class AIProviderInterface(ABC):
    """Abstract interface for all AI providers - scales to hundreds of models"""

    @abstractmethod
    async def generate_completion(
        self, prompt: str, config: AgentConfig, context: Optional[Dict[str, Any]] = None
    ) -> TaskResult:
        """Generate AI completion with enterprise monitoring"""
        pass

    @abstractmethod
    async def validate_config(self, config: AgentConfig) -> bool:
        """Validate provider-specific configuration"""
        pass

    @abstractmethod
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get model capabilities and pricing"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Provider health check for enterprise monitoring"""
        pass


class AgentServiceInterface(ABC):
    """Core agent service interface for enterprise orchestration"""

    @abstractmethod
    async def create_agent(self, config: AgentConfig, tenant_id: str) -> str:
        """Create agent with tenant isolation"""
        pass

    @abstractmethod
    async def execute_task(self, task: TaskRequest, tenant_id: str) -> TaskResult:
        """Execute task with enterprise monitoring"""
        pass

    @abstractmethod
    async def get_agent_analytics(
        self, agent_id: str, tenant_id: str
    ) -> Dict[str, Any]:
        """Get agent performance analytics"""
        pass


class WorkflowEngineInterface(ABC):
    """Interface for future Neural Workflow Engine"""

    @abstractmethod
    async def execute_workflow(
        self, workflow_definition: Dict[str, Any], tenant_id: str
    ) -> str:
        """Execute complex multi-agent workflow"""
        pass

    @abstractmethod
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow execution status"""
        pass


class AnalyticsEngineInterface(ABC):
    """Interface for future Cognitive Analytics Platform"""

    @abstractmethod
    async def track_event(
        self, event_type: str, data: Dict[str, Any], tenant_id: str
    ) -> None:
        """Track events for enterprise analytics"""
        pass

    @abstractmethod
    async def get_usage_analytics(
        self, tenant_id: str, time_range: Dict[str, datetime]
    ) -> Dict[str, Any]:
        """Get comprehensive usage analytics"""
        pass


# Enterprise Events for Event-Driven Architecture
class AgentEvent(BaseModel):
    """Base event class for enterprise event sourcing"""

    event_id: str = uuid.uuid4().hex
    event_type: str
    tenant_id: str
    agent_id: str
    timestamp: datetime = datetime.utcnow()
    data: Dict[str, Any] = {}

    # Enterprise audit trail
    user_id: Optional[str] = None
    source_service: str = "agent-service"
    trace_id: Optional[str] = None  # Future: Distributed tracing


# Provider Registry for Multi-Cloud AI
class ProviderRegistry:
    """Registry for managing multiple AI providers - scales to enterprise"""

    def __init__(self):
        self._providers: Dict[ProviderType, AIProviderInterface] = {}
        self._fallback_chain: List[ProviderType] = []

    def register_provider(
        self, provider_type: ProviderType, provider: AIProviderInterface
    ):
        """Register AI provider for multi-cloud setup"""
        self._providers[provider_type] = provider

    def get_provider(self, provider_type: ProviderType) -> AIProviderInterface:
        """Get provider with fallback support"""
        if provider_type in self._providers:
            return self._providers[provider_type]
        raise ValueError(f"Provider {provider_type} not registered")

    def set_fallback_chain(self, providers: List[ProviderType]):
        """Set provider fallback chain for enterprise resilience"""
        self._fallback_chain = providers

    async def execute_with_fallback(
        self, provider_type: ProviderType, operation: str, **kwargs
    ) -> Any:
        """Execute operation with automatic provider fallback"""
        providers_to_try = [provider_type] + self._fallback_chain

        for provider in providers_to_try:
            if provider in self._providers:
                try:
                    provider_instance = self._providers[provider]
                    if operation == "generate_completion":
                        return await provider_instance.generate_completion(**kwargs)
                    # Add more operations as needed
                except Exception as e:
                    # Log error and try next provider
                    continue

        raise Exception("All providers failed")


# Enterprise Configuration Management
class EnterpriseConfig:
    """Configuration management for enterprise deployment"""

    # Provider configurations
    PROVIDER_CONFIGS = {
        ProviderType.OPENROUTER: {
            "base_url": "https://openrouter.ai/api/v1",
            "default_model": "anthropic/claude-3-haiku",
            "rate_limit": {"requests_per_minute": 1000, "tokens_per_minute": 100000},
            "cost_per_token": {"input": 0.00025, "output": 0.00125},
            "features": ["completion", "streaming", "function_calling"],
        },
        # Future provider configs will be added here
    }

    # Agent type configurations
    AGENT_TYPE_CONFIGS = {
        AgentType.CHATBOT: {
            "default_model": "anthropic/claude-3-haiku",
            "default_temperature": 0.7,
            "max_tokens": 1000,
            "system_prompt_template": "You are a helpful AI assistant.",
        },
        AgentType.CONTENT_GENERATOR: {
            "default_model": "anthropic/claude-3-sonnet",
            "default_temperature": 0.9,
            "max_tokens": 2000,
            "system_prompt_template": "You are a creative content generator.",
        },
        AgentType.DATA_PROCESSOR: {
            "default_model": "anthropic/claude-3-haiku",
            "default_temperature": 0.1,
            "max_tokens": 1500,
            "system_prompt_template": "You are a data processing assistant.",
        },
    }
