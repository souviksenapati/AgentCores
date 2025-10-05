"""Enterprise Agent Service - Corrected Implementation"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger
from sqlalchemy.orm import Session

from app.core.interfaces import (
    AgentConfig,
    AgentServiceInterface,
    AgentType,
    ProviderRegistry,
    ProviderType,
    TaskRequest,
    TaskResult,
)
from app.core.interfaces import TaskStatus as InterfaceTaskStatus
from app.models.database import Agent as AgentModel
from app.models.database import AgentStatus as DBAgentStatus
from app.models.database import Task as TaskModel
from app.models.database import TaskPriority
from app.models.database import TaskStatus as DBTaskStatus
from app.models.database import TaskType, Tenant, TenantStatus, User
from app.schemas import Agent, AgentCreate
from app.schemas import AgentStatus as SchemaAgentStatus
from app.schemas import AgentUpdate, Task, TaskCreate, TaskExecution
from app.schemas import TaskStatus as SchemaTaskStatus
from app.services.event_service import EventService, EventType

# Status mappings between different representations
_AGENT_STATUS_DB_TO_SCHEMA = {
    DBAgentStatus.ACTIVE: SchemaAgentStatus.RUNNING,
    DBAgentStatus.INACTIVE: SchemaAgentStatus.IDLE,
    DBAgentStatus.ARCHIVED: SchemaAgentStatus.TERMINATED,
}

_AGENT_STATUS_SCHEMA_TO_DB = {
    SchemaAgentStatus.RUNNING: DBAgentStatus.ACTIVE,
    SchemaAgentStatus.IDLE: DBAgentStatus.INACTIVE,
    SchemaAgentStatus.PAUSED: DBAgentStatus.INACTIVE,
    SchemaAgentStatus.ERROR: DBAgentStatus.INACTIVE,
    SchemaAgentStatus.TERMINATED: DBAgentStatus.ARCHIVED,
}

_TASK_STATUS_DB_TO_SCHEMA = {
    DBTaskStatus.PENDING: SchemaTaskStatus.PENDING,
    DBTaskStatus.RUNNING: SchemaTaskStatus.RUNNING,
    DBTaskStatus.COMPLETED: SchemaTaskStatus.COMPLETED,
    DBTaskStatus.FAILED: SchemaTaskStatus.FAILED,
    DBTaskStatus.CANCELLED: SchemaTaskStatus.CANCELLED,
}

_TASK_STATUS_INTERFACE_TO_DB = {
    InterfaceTaskStatus.PENDING: DBTaskStatus.PENDING,
    InterfaceTaskStatus.RUNNING: DBTaskStatus.RUNNING,
    InterfaceTaskStatus.COMPLETED: DBTaskStatus.COMPLETED,
    InterfaceTaskStatus.FAILED: DBTaskStatus.FAILED,
    InterfaceTaskStatus.CANCELLED: DBTaskStatus.CANCELLED,
    InterfaceTaskStatus.RETRYING: DBTaskStatus.PENDING,
}


class AgentService(AgentServiceInterface):
    """Corrected Enterprise Agent Service"""

    def __init__(self, db: Session):
        self.db = db
        self.provider_registry = ProviderRegistry()
        self.event_service = EventService()
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize AI providers"""
        try:
            from app.providers.openrouter_provider import OpenRouterProvider

            self.provider_registry.register_provider(
                ProviderType.OPENROUTER, OpenRouterProvider()
            )
        except Exception as e:
            logger.warning(f"Failed to initialize OpenRouter provider: {e}")

    # Interface implementation
    async def create_agent(self, config: AgentConfig, tenant_id: str) -> str:
        """Create agent with tenant isolation"""
        try:
            # Get default user for tenant
            user = await self._get_default_user(tenant_id)
            await self._validate_tenant_access(tenant_id)

            # Create agent configuration
            config_data = {
                "agent_type": config.agent_type.value,
                "provider": config.provider.value,
                "tags": config.tags,
                "compliance_tags": config.compliance_tags,
                "resource_limits": config.resource_limits,
                "sla_requirements": config.sla_requirements,
            }

            db_agent = AgentModel(
                name=config.name,
                description=config.description,
                status=DBAgentStatus.INACTIVE,
                config=config_data,
                tenant_id=tenant_id,
                user_id=user.id,
                model=config.model,
                instructions=config.system_prompt,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                connected_agents=[],
            )

            self.db.add(db_agent)
            self.db.commit()
            self.db.refresh(db_agent)

            # Publish event
            await self._publish_event(
                EventType.AGENT_CREATED,
                tenant_id,
                {"agent_id": str(db_agent.agent_id), "name": config.name},
            )

            logger.info(f"Agent {db_agent.agent_id} created for tenant {tenant_id}")
            return str(db_agent.agent_id)

        except Exception as e:
            logger.error(f"Agent creation failed: {str(e)}")
            self.db.rollback()
            raise

    async def execute_task(self, task: TaskRequest, tenant_id: str) -> TaskResult:
        """Execute task with enterprise monitoring"""
        start_time = datetime.utcnow()
        task_id = uuid.uuid4().hex

        try:
            # Get agent from database
            db_agent = await self._get_agent_by_id(task.agent_id, tenant_id)
            if not db_agent:
                raise ValueError(
                    f"Agent {task.agent_id} not found in tenant {tenant_id}"
                )

            # Determine provider type
            config_data = db_agent.config or {}
            provider_type_str = config_data.get("provider", "openrouter")
            try:
                provider_type = ProviderType(provider_type_str)
            except ValueError:
                provider_type = ProviderType.OPENROUTER

            # Get provider
            provider = self.provider_registry.get_provider(provider_type)

            # Create agent configuration
            agent_config = AgentConfig(
                name=getattr(db_agent, "name", ""),
                description=getattr(db_agent, "description", "") or "",
                agent_type=AgentType(config_data.get("agent_type", "chatbot")),
                provider=provider_type,
                model=getattr(db_agent, "model", "anthropic/claude-3-haiku")
                or "anthropic/claude-3-haiku",
                system_prompt=getattr(
                    db_agent, "instructions", "You are a helpful AI assistant."
                )
                or "You are a helpful AI assistant.",
                temperature=getattr(db_agent, "temperature", 0.7) or 0.7,
                max_tokens=getattr(db_agent, "max_tokens", 1000) or 1000,
                tags=config_data.get("tags", []),
                compliance_tags=config_data.get("compliance_tags", []),
                resource_limits=config_data.get("resource_limits", {}),
                sla_requirements=config_data.get("sla_requirements", {}),
            )

            # Extract prompt from input data
            prompt = self._extract_prompt(task.input_data)

            # Execute with provider
            context = {
                "task_id": task_id,
                "agent_id": task.agent_id,
                "tenant_id": tenant_id,
            }
            result = await provider.generate_completion(
                prompt=prompt, config=agent_config, context=context
            )

            # Update agent stats
            current_total = getattr(db_agent, "total_tasks", 0) or 0
            setattr(db_agent, "total_tasks", current_total + 1)

            if result.status == InterfaceTaskStatus.COMPLETED:
                current_success = getattr(db_agent, "successful_tasks", 0) or 0
                setattr(db_agent, "successful_tasks", current_success + 1)
            elif result.status == InterfaceTaskStatus.FAILED:
                current_failed = getattr(db_agent, "failed_tasks", 0) or 0
                setattr(db_agent, "failed_tasks", current_failed + 1)

            setattr(db_agent, "updated_at", datetime.utcnow())
            self.db.commit()

            # Publish event
            await self._publish_event(
                EventType.TASK_COMPLETED,
                tenant_id,
                {
                    "task_id": task_id,
                    "agent_id": task.agent_id,
                    "status": result.status.value,
                    "execution_time_ms": result.execution_time_ms,
                },
            )

            return result

        except Exception as e:
            logger.error(f"Task execution failed: {str(e)}")
            completed_at = datetime.utcnow()
            execution_time_ms = int((completed_at - start_time).total_seconds() * 1000)

            await self._publish_event(
                EventType.TASK_FAILED,
                tenant_id,
                {"task_id": task_id, "agent_id": task.agent_id, "error": str(e)},
            )

            return TaskResult(
                task_id=task_id,
                status=InterfaceTaskStatus.FAILED,
                result=None,
                error_message=str(e),
                started_at=start_time,
                completed_at=completed_at,
                execution_time_ms=execution_time_ms,
                token_usage={},
                cost_estimate=0.0,
            )

    async def get_agent_analytics(
        self, agent_id: str, tenant_id: str
    ) -> Dict[str, Any]:
        """Get agent performance analytics"""
        # Get basic stats from database
        agent_uuid = self._safe_uuid(agent_id)
        tasks_query = (
            self.db.query(TaskModel)
            .filter(TaskModel.agent_id == agent_uuid)
            .filter(TaskModel.tenant_id == tenant_id)
        )

        total_tasks = tasks_query.count()
        completed_tasks = tasks_query.filter(
            TaskModel.status == DBTaskStatus.COMPLETED
        ).count()
        failed_tasks = tasks_query.filter(
            TaskModel.status == DBTaskStatus.FAILED
        ).count()

        success_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0

        return {
            "agent_id": agent_id,
            "tenant_id": tenant_id,
            "period": "24h",
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": round(success_rate, 2),
            "last_updated": datetime.utcnow().isoformat(),
        }

    # API helper methods
    async def create_agent_from_schema(
        self, agent_data: AgentCreate, tenant_id: str, user_id: str
    ) -> Agent:
        """Create agent from API schema"""
        config = AgentConfig(
            name=agent_data.name,
            description=agent_data.description or "",
            agent_type=AgentType(agent_data.agent_type),
            provider=ProviderType.OPENROUTER,
            model=agent_data.model,
            system_prompt=agent_data.instructions or "You are a helpful AI assistant.",
            temperature=agent_data.temperature,
            max_tokens=agent_data.max_tokens,
            tags=agent_data.capabilities or [],
            compliance_tags=[],
            resource_limits=agent_data.resources or {},
            sla_requirements={},
        )

        agent_id = await self.create_agent(config, tenant_id)
        agent = await self.get_agent(agent_id, tenant_id)
        if not agent:
            raise ValueError(f"Failed to retrieve created agent {agent_id}")
        return agent

    async def get_agent(self, agent_id: str, tenant_id: str) -> Optional[Agent]:
        """Get agent by ID within tenant"""
        db_agent = await self._get_agent_by_id(agent_id, tenant_id)
        if not db_agent:
            return None
        return self._db_agent_to_schema(db_agent)

    async def get_agents(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[SchemaAgentStatus] = None,
        agent_type: Optional[str] = None,
    ) -> Tuple[List[Agent], int]:
        """Get agents with filtering"""
        query = self.db.query(AgentModel).filter(AgentModel.tenant_id == tenant_id)

        if status and status in _AGENT_STATUS_SCHEMA_TO_DB:
            db_status = _AGENT_STATUS_SCHEMA_TO_DB[status]
            query = query.filter(AgentModel.status == db_status)

        total = query.count()
        db_agents = (
            query.order_by(AgentModel.created_at.desc()).offset(skip).limit(limit).all()
        )

        agents = []
        for db_agent in db_agents:
            agent = self._db_agent_to_schema(db_agent)
            if agent_type and agent.agent_type.lower() != agent_type.lower():
                continue
            agents.append(agent)

        return agents, total

    async def update_agent(
        self, agent_id: str, tenant_id: str, update_data: AgentUpdate
    ) -> Optional[Agent]:
        """Update agent"""
        db_agent = await self._get_agent_by_id(agent_id, tenant_id)
        if not db_agent:
            return None

        if update_data.name is not None:
            setattr(db_agent, "name", update_data.name)
        if update_data.description is not None:
            setattr(db_agent, "description", update_data.description)
        if (
            update_data.status is not None
            and update_data.status in _AGENT_STATUS_SCHEMA_TO_DB
        ):
            setattr(db_agent, "status", _AGENT_STATUS_SCHEMA_TO_DB[update_data.status])
        if update_data.model is not None:
            setattr(db_agent, "model", update_data.model)
        if update_data.instructions is not None:
            setattr(db_agent, "instructions", update_data.instructions)
        if update_data.temperature is not None:
            setattr(db_agent, "temperature", update_data.temperature)
        if update_data.max_tokens is not None:
            setattr(db_agent, "max_tokens", update_data.max_tokens)
        if update_data.connected_agents is not None:
            setattr(db_agent, "connected_agents", update_data.connected_agents)

        config = getattr(db_agent, "config", {}) or {}
        if update_data.configuration is not None:
            config.update(update_data.configuration)
        if update_data.capabilities is not None:
            config["capabilities"] = update_data.capabilities
        if update_data.resources is not None:
            config["resources"] = update_data.resources

        setattr(db_agent, "config", config)
        setattr(db_agent, "updated_at", datetime.utcnow())

        self.db.commit()
        self.db.refresh(db_agent)

        await self._publish_event(
            EventType.AGENT_UPDATED,
            tenant_id,
            {"agent_id": agent_id, "name": db_agent.name},
        )

        return self._db_agent_to_schema(db_agent)

    async def delete_agent(self, agent_id: str, tenant_id: str) -> bool:
        """Delete (archive) agent"""
        db_agent = await self._get_agent_by_id(agent_id, tenant_id)
        if not db_agent:
            return False

        setattr(db_agent, "status", DBAgentStatus.ARCHIVED)
        setattr(db_agent, "updated_at", datetime.utcnow())
        self.db.commit()

        await self._publish_event(
            EventType.AGENT_DELETED,
            tenant_id,
            {"agent_id": agent_id, "name": db_agent.name},
        )

        return True

    async def start_agent(self, agent_id: str, tenant_id: str) -> Optional[Agent]:
        """Start agent"""
        db_agent = await self._get_agent_by_id(agent_id, tenant_id)
        if not db_agent:
            return None

        current_status = getattr(db_agent, "status", None)
        if current_status == DBAgentStatus.ACTIVE:
            return self._db_agent_to_schema(db_agent)

        setattr(db_agent, "status", DBAgentStatus.ACTIVE)
        setattr(db_agent, "updated_at", datetime.utcnow())
        self.db.commit()
        self.db.refresh(db_agent)

        await self._publish_event(
            EventType.AGENT_STARTED,
            tenant_id,
            {"agent_id": agent_id, "name": db_agent.name},
        )

        return self._db_agent_to_schema(db_agent)

    async def stop_agent(self, agent_id: str, tenant_id: str) -> Optional[Agent]:
        """Stop agent"""
        db_agent = await self._get_agent_by_id(agent_id, tenant_id)
        if not db_agent:
            return None

        current_status = getattr(db_agent, "status", None)
        if current_status == DBAgentStatus.INACTIVE:
            return self._db_agent_to_schema(db_agent)

        setattr(db_agent, "status", DBAgentStatus.INACTIVE)
        setattr(db_agent, "updated_at", datetime.utcnow())
        self.db.commit()
        self.db.refresh(db_agent)

        await self._publish_event(
            EventType.AGENT_STOPPED,
            tenant_id,
            {"agent_id": agent_id, "name": db_agent.name},
        )

        return self._db_agent_to_schema(db_agent)

    async def get_available_agents_for_connection(
        self, agent_id: str, tenant_id: str
    ) -> List[Dict[str, Any]]:
        """Get available agents for connection (excluding self)"""
        agent_uuid = self._safe_uuid(agent_id)
        agents = (
            self.db.query(AgentModel)
            .filter(AgentModel.tenant_id == tenant_id)
            .filter(AgentModel.agent_id != agent_uuid)
            .filter(AgentModel.status != DBAgentStatus.ARCHIVED)
            .all()
        )

        return [
            {
                "id": str(agent.agent_id),
                "name": agent.name,
                "description": agent.description,
                "status": _AGENT_STATUS_DB_TO_SCHEMA.get(
                    getattr(agent, "status", DBAgentStatus.INACTIVE),
                    SchemaAgentStatus.IDLE,
                ).value,
            }
            for agent in agents
        ]

    # Helper methods
    async def _get_agent_by_id(
        self, agent_id: str, tenant_id: str
    ) -> Optional[AgentModel]:
        """Get agent model by ID"""
        try:
            agent_uuid = self._safe_uuid(agent_id)
        except ValueError:
            return None

        return (
            self.db.query(AgentModel)
            .filter(AgentModel.agent_id == agent_uuid)
            .filter(AgentModel.tenant_id == tenant_id)
            .first()
        )

    def _db_agent_to_schema(self, db_agent: AgentModel) -> Agent:
        """Convert database agent to schema"""
        config = getattr(db_agent, "config", {}) or {}
        agent_id = getattr(db_agent, "agent_id", None)
        user_id = getattr(db_agent, "user_id", None)
        status = getattr(db_agent, "status", DBAgentStatus.INACTIVE)
        created_at = getattr(db_agent, "created_at", datetime.utcnow())
        updated_at = getattr(db_agent, "updated_at", datetime.utcnow())

        return Agent(
            id=str(agent_id) if agent_id else "",
            name=getattr(db_agent, "name", ""),
            description=getattr(db_agent, "description", ""),
            agent_type=config.get("agent_type", "chatbot"),
            model=getattr(db_agent, "model", ""),
            instructions=getattr(db_agent, "instructions", ""),
            temperature=getattr(db_agent, "temperature", 0.7),
            max_tokens=getattr(db_agent, "max_tokens", 1000),
            version="1.0.0",
            configuration=config,
            capabilities=config.get("capabilities", []),
            resources=config.get("resources", {}),
            connected_agents=getattr(db_agent, "connected_agents", []) or [],
            status=_AGENT_STATUS_DB_TO_SCHEMA.get(status, SchemaAgentStatus.IDLE),
            created_at=created_at,
            updated_at=updated_at,
            last_active=updated_at,
            created_by=str(user_id) if user_id else None,
        )

    async def _get_default_user(self, tenant_id: str) -> User:
        """Get default user for tenant"""
        user = (
            self.db.query(User)
            .filter(User.tenant_id == tenant_id)
            .filter(User.is_active.is_(True))
            .order_by(User.created_at.asc())
            .first()
        )
        if not user:
            raise ValueError(f"No active users found for tenant {tenant_id}")
        return user

    async def _validate_tenant_access(self, tenant_id: str):
        """Validate tenant access"""
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")
        if getattr(tenant, "status", None) != TenantStatus.ACTIVE:
            raise ValueError(f"Tenant {tenant_id} is not active")

    def _safe_uuid(self, value: str) -> uuid.UUID:
        """Safely convert string to UUID"""
        try:
            return uuid.UUID(value)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid UUID: {value}")

    def _extract_prompt(self, input_data: Any) -> str:
        """Extract prompt from input data"""
        if isinstance(input_data, str):
            return input_data
        elif isinstance(input_data, dict):
            return input_data.get("prompt", str(input_data))
        else:
            return str(input_data)

    async def _publish_event(
        self, event_type: EventType, tenant_id: str, data: Dict[str, Any]
    ):
        """Publish event safely"""
        try:
            event_data = {
                "type": event_type.value,
                "tenant_id": tenant_id,
                "timestamp": datetime.utcnow().isoformat(),
                **data,
            }
            await self.event_service.publish_event(
                event_data=event_data,
                event_type=event_type,
                tenant_id=tenant_id,
            )
        except Exception as e:
            logger.warning(f"Failed to publish event {event_type.value}: {e}")


class TaskService:
    """Enterprise Task Service"""

    def __init__(self, db: Session):
        self.db = db
        self.agent_service = AgentService(db)

    async def create_task(
        self, task_data: TaskCreate, tenant_id: str, user_id: str
    ) -> Task:
        """Create a new task"""
        # Verify agent exists
        agent_uuid = self.agent_service._safe_uuid(task_data.agent_id)
        agent = (
            self.db.query(AgentModel)
            .filter(AgentModel.agent_id == agent_uuid)
            .filter(AgentModel.tenant_id == tenant_id)
            .first()
        )
        if not agent:
            raise ValueError(
                f"Agent {task_data.agent_id} not found in tenant {tenant_id}"
            )

        # Create task
        user_uuid = self.agent_service._safe_uuid(user_id)

        # Map task type and priority
        task_type = TaskType.COMPLETION
        if hasattr(task_data, "task_type"):
            type_mapping = {
                "completion": TaskType.COMPLETION,
                "analysis": TaskType.ANALYSIS,
                "workflow": TaskType.WORKFLOW,
                "integration": TaskType.INTEGRATION,
            }
            task_type = type_mapping.get(
                task_data.task_type.lower(), TaskType.COMPLETION
            )

        priority_mapping = {
            1: TaskPriority.LOW,
            2: TaskPriority.NORMAL,
            3: TaskPriority.NORMAL,
            4: TaskPriority.HIGH,
            5: TaskPriority.URGENT,
        }
        priority = priority_mapping.get(
            getattr(task_data, "priority", 3), TaskPriority.NORMAL
        )

        db_task = TaskModel(
            task_type=task_type,
            priority=priority,
            status=DBTaskStatus.PENDING,
            input_data={
                "name": task_data.name,
                "description": task_data.description,
                "data": task_data.input_data,
            },
            timeout_seconds=getattr(task_data, "timeout_seconds", 300),
            max_retries=getattr(task_data, "retry_count", 3),
            tenant_id=tenant_id,
            agent_id=agent_uuid,
            user_id=user_uuid,
            provider=(
                getattr(agent, "config", {}).get("provider", "openrouter")
                if getattr(agent, "config", None)
                else "openrouter"
            ),
            model=agent.model,
        )

        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)

        logger.info(
            f"Created task {db_task.task_id} for agent {task_data.agent_id} in tenant {tenant_id}"
        )
        return self._db_task_to_schema(db_task)

    async def get_task(self, task_id: str, tenant_id: str) -> Optional[Task]:
        """Get task by ID within tenant"""
        try:
            task_uuid = uuid.UUID(task_id)
        except ValueError:
            return None

        db_task = (
            self.db.query(TaskModel)
            .filter(TaskModel.task_id == task_uuid)
            .filter(TaskModel.tenant_id == tenant_id)
            .first()
        )
        return self._db_task_to_schema(db_task) if db_task else None

    async def get_tasks(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        agent_id: Optional[str] = None,
    ) -> Tuple[List[Task], int]:
        """Get tasks with filtering within tenant"""
        query = self.db.query(TaskModel).filter(TaskModel.tenant_id == tenant_id)

        if agent_id:
            try:
                agent_uuid = self.agent_service._safe_uuid(agent_id)
                query = query.filter(TaskModel.agent_id == agent_uuid)
            except ValueError:
                return [], 0

        total = query.count()
        db_tasks = (
            query.order_by(TaskModel.created_at.desc()).offset(skip).limit(limit).all()
        )

        tasks = [self._db_task_to_schema(db_task) for db_task in db_tasks]
        return tasks, total

    async def execute_task(self, task_id: str, tenant_id: str) -> TaskExecution:
        """Execute a task"""
        # Get task
        try:
            task_uuid = uuid.UUID(task_id)
        except ValueError:
            raise ValueError(f"Invalid task ID: {task_id}")

        db_task = (
            self.db.query(TaskModel)
            .filter(TaskModel.task_id == task_uuid)
            .filter(TaskModel.tenant_id == tenant_id)
            .first()
        )
        if not db_task:
            raise ValueError(f"Task {task_id} not found in tenant {tenant_id}")

        # Update task status
        setattr(db_task, "started_at", datetime.utcnow())
        setattr(db_task, "status", DBTaskStatus.RUNNING)
        self.db.commit()
        self.db.refresh(db_task)

        try:
            # Create task request
            input_data = db_task.input_data or {}
            task_request = TaskRequest(
                agent_id=str(db_task.agent_id),
                input_data=input_data.get("data", {}),
                task_type="completion",
                priority=5,
                timeout_seconds=getattr(db_task, "timeout_seconds", 300) or 300,
                retry_policy={"max_retries": db_task.max_retries or 3},
                context={"task_id": str(db_task.task_id), "tenant_id": tenant_id},
            )

            # Execute through agent service
            result = await self.agent_service.execute_task(task_request, tenant_id)

            # Update task with results
            setattr(
                db_task,
                "status",
                _TASK_STATUS_INTERFACE_TO_DB.get(result.status, DBTaskStatus.FAILED),
            )
            setattr(db_task, "completed_at", result.completed_at or datetime.utcnow())
            setattr(db_task, "execution_time_ms", result.execution_time_ms)
            setattr(
                db_task,
                "result",
                (
                    {"output": result.result}
                    if isinstance(result.result, str)
                    else result.result
                ),
            )
            setattr(db_task, "error_message", result.error_message)
            setattr(db_task, "token_usage", result.token_usage or {})
            setattr(db_task, "cost_estimate", result.cost_estimate or 0.0)

            self.db.commit()
            self.db.refresh(db_task)

            task_id_val = getattr(db_task, "task_id", None)
            agent_id_val = getattr(db_task, "agent_id", None)
            status = getattr(db_task, "status", DBTaskStatus.FAILED)

            return TaskExecution(
                id=str(task_id_val) if task_id_val else "",
                agent_id=str(agent_id_val) if agent_id_val else "",
                task_id=str(task_id_val) if task_id_val else "",
                status=_TASK_STATUS_DB_TO_SCHEMA.get(status, SchemaTaskStatus.FAILED),
                result=getattr(db_task, "result", None),
                error_message=getattr(db_task, "error_message", None),
                execution_time_ms=getattr(db_task, "execution_time_ms", None),
                started_at=getattr(db_task, "started_at", None),
                completed_at=getattr(db_task, "completed_at", None),
                created_at=getattr(db_task, "created_at", datetime.utcnow()),
            )

        except Exception as e:
            # Update task with error
            setattr(db_task, "status", DBTaskStatus.FAILED)
            setattr(db_task, "completed_at", datetime.utcnow())
            setattr(db_task, "error_message", str(e))
            self.db.commit()
            raise

    def _db_task_to_schema(self, db_task: TaskModel) -> Task:
        """Convert database task to schema"""
        input_data = getattr(db_task, "input_data", {}) or {}
        task_id = getattr(db_task, "task_id", None)
        agent_id = getattr(db_task, "agent_id", None)
        task_type = getattr(db_task, "task_type", TaskType.COMPLETION)
        priority = getattr(db_task, "priority", TaskPriority.NORMAL)

        return Task(
            id=str(task_id) if task_id else "",
            agent_id=str(agent_id) if agent_id else "",
            name=input_data.get("name", f"Task {task_id}") if task_id else "Task",
            description=input_data.get("description"),
            task_type=(
                task_type.value.lower()
                if hasattr(task_type, "value")
                else str(task_type).lower()
            ),
            input_data=input_data.get("data", {}),
            output_schema=None,
            priority={
                TaskPriority.LOW: 1,
                TaskPriority.NORMAL: 3,
                TaskPriority.HIGH: 4,
                TaskPriority.URGENT: 5,
            }.get(priority, 3),
            timeout_seconds=getattr(db_task, "timeout_seconds", 300) or 300,
            retry_count=getattr(db_task, "max_retries", 3) or 3,
            created_at=getattr(db_task, "created_at", datetime.utcnow()),
            updated_at=getattr(db_task, "updated_at", datetime.utcnow()),
        )
