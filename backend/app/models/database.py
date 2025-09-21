from sqlalchemy import Column, String, DateTime, Integer, Text, JSON, Enum, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid

Base = declarative_base()

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
    
    # Relationships
    tasks = relationship("Task", back_populates="agent")
    executions = relationship("TaskExecution", back_populates="agent")

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
    
    # Relationships
    agent = relationship("Agent", back_populates="tasks")
    executions = relationship("TaskExecution", back_populates="task")

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
    
    # Relationships
    agent = relationship("Agent", back_populates="executions")
    task = relationship("Task", back_populates="executions")

class AgentMetrics(Base):
    __tablename__ = "agent_metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
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