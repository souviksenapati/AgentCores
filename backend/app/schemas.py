from pydantic import BaseModel, Field
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

# Agent Schemas
class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    agent_type: str = Field(..., description="Type of agent (gpt-4, claude, custom)")
    version: str = Field(default="1.0.0")
    configuration: Optional[Dict[str, Any]] = Field(default_factory=dict)
    capabilities: Optional[List[str]] = Field(default_factory=list)
    resources: Optional[Dict[str, Any]] = Field(default_factory=dict)

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