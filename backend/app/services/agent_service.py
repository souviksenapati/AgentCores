from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
import asyncio
import httpx
from loguru import logger

from app.models.database import Agent, Task, TaskExecution, AgentStatus, TaskStatus
from app.schemas import AgentCreate, AgentUpdate, TaskCreate, TaskUpdate

class AgentService:
    def __init__(self, db: Session):
        self.db = db

    async def create_agent(self, agent_data: AgentCreate) -> Agent:
        """Create a new agent"""
        db_agent = Agent(**agent_data.model_dump())
        self.db.add(db_agent)
        self.db.commit()
        self.db.refresh(db_agent)
        
        logger.info(f"Created agent {db_agent.id} of type {db_agent.agent_type}")
        return db_agent

    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        return self.db.query(Agent).filter(Agent.id == agent_id).first()

    async def get_agents(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[AgentStatus] = None,
        agent_type: Optional[str] = None
    ) -> tuple[List[Agent], int]:
        """Get agents with filtering"""
        query = self.db.query(Agent)
        
        if status:
            query = query.filter(Agent.status == status)
        if agent_type:
            query = query.filter(Agent.agent_type == agent_type)
            
        total = query.count()
        agents = query.offset(skip).limit(limit).all()
        
        return agents, total

    async def update_agent(self, agent_id: str, agent_data: AgentUpdate) -> Optional[Agent]:
        """Update agent"""
        db_agent = await self.get_agent(agent_id)
        if not db_agent:
            return None
            
        update_data = agent_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_agent, field, value)
            
        db_agent.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_agent)
        
        logger.info(f"Updated agent {agent_id}")
        return db_agent

    async def delete_agent(self, agent_id: str) -> bool:
        """Delete agent"""
        db_agent = await self.get_agent(agent_id)
        if not db_agent:
            return False
            
        # Set status to terminated instead of hard delete
        db_agent.status = AgentStatus.TERMINATED
        db_agent.updated_at = datetime.utcnow()
        self.db.commit()
        
        logger.info(f"Terminated agent {agent_id}")
        return True

    async def start_agent(self, agent_id: str) -> Optional[Agent]:
        """Start an agent"""
        db_agent = await self.get_agent(agent_id)
        if not db_agent:
            return None
            
        if db_agent.status not in [AgentStatus.IDLE, AgentStatus.PAUSED]:
            raise ValueError(f"Cannot start agent in {db_agent.status} status")
            
        db_agent.status = AgentStatus.RUNNING
        db_agent.last_active = datetime.utcnow()
        db_agent.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_agent)
        
        logger.info(f"Started agent {agent_id}")
        return db_agent

    async def stop_agent(self, agent_id: str) -> Optional[Agent]:
        """Stop an agent"""
        db_agent = await self.get_agent(agent_id)
        if not db_agent:
            return None
            
        db_agent.status = AgentStatus.IDLE
        db_agent.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_agent)
        
        logger.info(f"Stopped agent {agent_id}")
        return db_agent

class TaskService:
    def __init__(self, db: Session):
        self.db = db

    async def create_task(self, task_data: TaskCreate) -> Task:
        """Create a new task"""
        # Verify agent exists
        agent = self.db.query(Agent).filter(Agent.id == task_data.agent_id).first()
        if not agent:
            raise ValueError(f"Agent {task_data.agent_id} not found")
            
        db_task = Task(**task_data.model_dump())
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        
        logger.info(f"Created task {db_task.id} for agent {task_data.agent_id}")
        return db_task

    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self.db.query(Task).filter(Task.id == task_id).first()

    async def get_tasks(
        self,
        skip: int = 0,
        limit: int = 100,
        agent_id: Optional[str] = None
    ) -> tuple[List[Task], int]:
        """Get tasks with filtering"""
        query = self.db.query(Task)
        
        if agent_id:
            query = query.filter(Task.agent_id == agent_id)
            
        total = query.count()
        tasks = query.offset(skip).limit(limit).all()
        
        return tasks, total

    async def execute_task(self, task_id: str) -> TaskExecution:
        """Execute a task"""
        task = await self.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
            
        agent = self.db.query(Agent).filter(Agent.id == task.agent_id).first()
        if not agent:
            raise ValueError(f"Agent {task.agent_id} not found")
            
        if agent.status != AgentStatus.RUNNING:
            raise ValueError(f"Agent {agent.id} is not running")

        # Create execution record
        execution = TaskExecution(
            agent_id=task.agent_id,
            task_id=task.id,
            status=TaskStatus.RUNNING,
            started_at=datetime.utcnow()
        )
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)

        try:
            # Execute the task based on type
            start_time = datetime.utcnow()
            result = await self._execute_task_by_type(agent, task)
            end_time = datetime.utcnow()
            
            # Update execution with success
            execution.status = TaskStatus.COMPLETED
            execution.result = result
            execution.completed_at = end_time
            execution.execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Update agent last active
            agent.last_active = end_time
            
        except Exception as e:
            # Update execution with failure
            execution.status = TaskStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            logger.error(f"Task {task_id} failed: {str(e)}")
            
        self.db.commit()
        self.db.refresh(execution)
        
        return execution

    async def _execute_task_by_type(self, agent: Agent, task: Task) -> dict:
        """Execute task based on its type"""
        if task.task_type == "text_processing":
            return await self._execute_text_processing(agent, task)
        elif task.task_type == "api_call":
            return await self._execute_api_call(agent, task)
        elif task.task_type == "workflow":
            return await self._execute_workflow(agent, task)
        else:
            raise ValueError(f"Unknown task type: {task.task_type}")

    async def _execute_text_processing(self, agent: Agent, task: Task) -> dict:
        """Execute text processing task"""
        input_text = task.input_data.get("text", "")
        operation = task.input_data.get("operation", "echo")
        
        if operation == "echo":
            result = input_text
        elif operation == "uppercase":
            result = input_text.upper()
        elif operation == "lowercase":
            result = input_text.lower()
        elif operation == "word_count":
            result = len(input_text.split())
        else:
            raise ValueError(f"Unknown text operation: {operation}")
            
        return {
            "operation": operation,
            "input": input_text,
            "output": result,
            "processed_by": agent.id
        }

    async def _execute_api_call(self, agent: Agent, task: Task) -> dict:
        """Execute API call task"""
        url = task.input_data.get("url")
        method = task.input_data.get("method", "GET")
        headers = task.input_data.get("headers", {})
        data = task.input_data.get("data")
        
        if not url:
            raise ValueError("URL is required for api_call task")
            
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                timeout=task.timeout_seconds
            )
            
        return {
            "url": url,
            "method": method,
            "status_code": response.status_code,
            "response": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
            "processed_by": agent.id
        }

    async def _execute_workflow(self, agent: Agent, task: Task) -> dict:
        """Execute workflow task"""
        steps = task.input_data.get("steps", [])
        results = []
        
        for step in steps:
            step_result = await self._execute_workflow_step(agent, step)
            results.append(step_result)
            
        return {
            "workflow_results": results,
            "processed_by": agent.id
        }

    async def _execute_workflow_step(self, agent: Agent, step: dict) -> dict:
        """Execute a single workflow step"""
        step_type = step.get("type")
        
        if step_type == "delay":
            delay_seconds = step.get("seconds", 1)
            await asyncio.sleep(delay_seconds)
            return {"type": "delay", "seconds": delay_seconds}
        elif step_type == "log":
            message = step.get("message", "Workflow step executed")
            logger.info(f"Workflow step: {message}")
            return {"type": "log", "message": message}
        else:
            return {"type": "unknown", "step": step}