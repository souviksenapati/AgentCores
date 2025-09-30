"""Enterprise Agent Service - Clean Implementation"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
from loguru import logger

from app.models.database import Task, Tenant, AgentStatus, TaskStatus, TenantStatus
from app.schemas import AgentCreate, AgentUpdate, TaskCreate, TaskUpdate
from app.core.interfaces import (
    AgentServiceInterface, AgentConfig, TaskRequest, TaskResult,
    AgentType, AgentStatus as InterfaceAgentStatus, TaskStatus as InterfaceTaskStatus, 
    ProviderType, AgentEvent, ProviderRegistry
)
from app.services.event_service import EventService


class AgentService(AgentServiceInterface):
    """Enterprise Agent Service with Neural Orchestration DNA"""
    
    def __init__(self, db: Session):
        self.db = db
        self.provider_registry = ProviderRegistry()
        self.event_service = EventService()
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize AI providers"""
        from app.providers.openrouter_provider import OpenRouterProvider
        self.provider_registry.register_provider(ProviderType.OPENROUTER, OpenRouterProvider())

    async def create_agent_from_config(self, config: AgentConfig, tenant_id: str, user_id: str) -> str:
        """Create agent from enterprise configuration"""
        agent_data = AgentCreate(
            name=config.name,
            description=config.description,
            agent_type=config.agent_type.value,
            model=config.model,
            instructions=config.instructions,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )
        agent = await self.create_agent(agent_data, tenant_id, user_id)
        return agent.id

    async def create_agent(self, agent_data: AgentCreate, tenant_id: str, user_id: str = None) -> Agent:
        """Create agent with enterprise patterns"""
        try:
            await self._validate_tenant_access(tenant_id, user_id or "system")
            
            # Import Agent model here to avoid circular imports
            from app.models.database import Agent as AgentModel
            
            agent_dict = {
                "name": agent_data.name,
                "description": agent_data.description,
                "status": "idle",
                "config": agent_data.configuration or {},
                "tenant_id": tenant_id,
                "user_id": user_id,
                "model": getattr(agent_data, 'model', 'openrouter/meta-llama/llama-3.2-3b-instruct:free'),
                "instructions": getattr(agent_data, 'instructions', 'You are a helpful AI assistant.'),
                "temperature": getattr(agent_data, 'temperature', 0.7),
                "max_tokens": getattr(agent_data, 'max_tokens', 1000),
                "connected_agents": getattr(agent_data, 'connected_agents', [])
            }
            
            db_agent = AgentModel(**agent_dict)
            self.db.add(db_agent)
            self.db.commit()
            self.db.refresh(db_agent)
            
            logger.info(f"Enterprise agent {db_agent.agent_id} created for tenant {tenant_id}")
            return db_agent
            
        except Exception as e:
            logger.error(f"Agent creation failed: {str(e)}")
            self.db.rollback()
            raise

    async def execute_task(self, agent_id: str, task_request: TaskRequest, tenant_id: str) -> TaskResult:
        """Execute task with enterprise orchestration"""
        try:
            agent = await self.get_agent(agent_id, tenant_id)
            if not agent:
                raise ValueError(f"Agent {agent_id} not found in tenant {tenant_id}")
            
            provider_type = ProviderType(agent.model.split('/')[0] if '/' in agent.model else "openrouter")
            provider = self.provider_registry.get_provider(provider_type)
            
            if not provider:
                raise ValueError(f"No provider available for {provider_type}")
            
            start_time = datetime.utcnow()
            result = await provider.execute_task(
                agent_id=agent_id,
                task_request=task_request,
                agent_config=AgentConfig(
                    name=agent.name,
                    description=agent.description,
                    agent_type=AgentType(agent.agent_type),
                    provider=provider_type,
                    model=agent.model,
                    instructions=agent.instructions or "",
                    temperature=getattr(agent, 'temperature', 0.7),
                    max_tokens=getattr(agent, 'max_tokens', 1000)
                )
            )
            
            agent.last_active = datetime.utcnow()
            self.db.commit()
            
            execution_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            await self.event_service.emit_event(
                AgentEvent(
                    event_type="task_completed",
                    agent_id=agent_id,
                    tenant_id=tenant_id,
                    metadata={
                        "task_type": task_request.task_type.value,
                        "status": result.status.value,
                        "execution_time_ms": execution_time_ms,
                        "cost_estimate": result.cost_estimate,
                        "token_usage": result.token_usage
                    }
                )
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Task execution failed: {str(e)}")
            return TaskResult(
                task_id=task_request.task_id,
                status=InterfaceTaskStatus.FAILED,
                result=None,
                error_message=str(e),
                execution_time_ms=0,
                cost_estimate=0.0
            )

    async def get_agent(self, agent_id: str, tenant_id: str) -> Optional[Agent]:
        """Get agent by ID within tenant"""
        from app.models.database import Agent as AgentModel
        return self.db.query(AgentModel).filter(
            AgentModel.agent_id == agent_id,
            AgentModel.tenant_id == tenant_id
        ).first()

    async def list_agents(self, tenant_id: str, user_id: str) -> List[Dict[str, Any]]:
        """List agents for tenant"""
        from app.models.database import Agent as AgentModel
        agents = self.db.query(AgentModel).filter(AgentModel.tenant_id == tenant_id).all()
        
        return [
            {
                "id": str(agent.agent_id),
                "agent_id": str(agent.agent_id),
                "name": agent.name,
                "description": agent.description,
                "agent_type": agent.config.get("agent_type", "conversational"),
                "status": agent.status.value,
                "model": getattr(agent, 'model', 'openrouter/meta-llama/llama-3.2-3b-instruct:free'),
                "instructions": getattr(agent, 'instructions', 'You are a helpful AI assistant.'),
                "temperature": getattr(agent, 'temperature', 0.7),
                "max_tokens": getattr(agent, 'max_tokens', 1000),
                "connected_agents": getattr(agent, 'connected_agents', []),
                "created_at": agent.created_at,
                "last_active": agent.last_active
            }
            for agent in agents
        ]

    async def get_available_agents_for_connection(self, agent_id: str, tenant_id: str) -> List[Dict[str, Any]]:
        """Get available agents for connection (excluding self)"""
        from app.models.database import Agent as AgentModel
        agents = self.db.query(AgentModel).filter(
            AgentModel.tenant_id == tenant_id,
            AgentModel.agent_id != agent_id
        ).all()
        
        return [
            {
                "id": str(agent.agent_id),
                "name": agent.name,
                "description": agent.description,
                "status": agent.status.value
            }
            for agent in agents
        ]

    async def get_agent_analytics(self, agent_id: str, tenant_id: str, period: str = "24h") -> Dict[str, Any]:
        """Get analytics for agent"""
        end_time = datetime.utcnow()
        if period == "1h":
            start_time = end_time - timedelta(hours=1)
        elif period == "24h":
            start_time = end_time - timedelta(hours=24)
        elif period == "7d":
            start_time = end_time - timedelta(days=7)
        else:
            start_time = end_time - timedelta(hours=24)
        
        return await self.event_service.get_analytics_summary(
            tenant_id=tenant_id,
            start_time=start_time,
            end_time=end_time,
            agent_id=agent_id
        )

    async def _validate_tenant_access(self, tenant_id: str, user_id: str):
        """Validate tenant access"""
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")
        if tenant.status != TenantStatus.ACTIVE:
            raise ValueError(f"Tenant {tenant_id} is not active")


class TaskService:
    """Enterprise Task Service"""
    
    def __init__(self, db: Session):
        self.db = db

    async def create_task(self, task_data: TaskCreate, tenant_id: str) -> Task:
        """Create a new task"""
        from app.models.database import Agent as AgentModel
        agent = self.db.query(AgentModel).filter(
            AgentModel.agent_id == task_data.agent_id,
            AgentModel.tenant_id == tenant_id
        ).first()
        if not agent:
            raise ValueError(f"Agent {task_data.agent_id} not found in tenant {tenant_id}")
            
        task_dict = task_data.model_dump()
        task_dict["tenant_id"] = tenant_id
        
        db_task = Task(**task_dict)
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        
        logger.info(f"Created task {db_task.task_id} for agent {task_data.agent_id} in tenant {tenant_id}")
        return db_task

    async def get_task(self, task_id: str, tenant_id: str) -> Optional[Task]:
        """Get task by ID within tenant"""
        return self.db.query(Task).filter(
            Task.task_id == task_id,
            Task.tenant_id == tenant_id
        ).first()

    async def get_tasks(self, tenant_id: str, skip: int = 0, limit: int = 100, agent_id: Optional[str] = None) -> tuple[List[Task], int]:
        """Get tasks with filtering within tenant"""
        query = self.db.query(Task).filter(Task.tenant_id == tenant_id)
        
        if agent_id:
            query = query.filter(Task.agent_id == agent_id)
            
        total = query.count()
        tasks = query.offset(skip).limit(limit).all()
        
        return tasks, total