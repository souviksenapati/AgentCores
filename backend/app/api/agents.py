from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas import (
    Agent, AgentCreate, AgentUpdate, AgentListResponse,
    Task, TaskCreate, TaskUpdate, TaskListResponse,
    TaskExecution, TaskExecutionResponse,
    AgentStatus, TaskStatus, UserResponse,
    ChatRequest, ChatResponse, ChatMessage
)
from app.services.agent_service import AgentService, TaskService
from app.auth import get_current_user, get_tenant_id, require_admin_or_member_role
from app.models.database import User
from app.models.chat import ChatMessage as ChatMessageModel

router = APIRouter()

# Agent Endpoints
@router.post("/agents", response_model=Agent, status_code=201)
async def create_agent(
    agent_data: AgentCreate,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(require_admin_or_member_role),
    db: Session = Depends(get_db)
):
    """Create a new agent"""
    service = AgentService(db)
    return await service.create_agent(agent_data, tenant_id)

@router.get("/agents", response_model=AgentListResponse)
async def get_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[AgentStatus] = None,
    agent_type: Optional[str] = None,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all agents with filtering"""
    service = AgentService(db)
    agents, total = await service.get_agents(tenant_id, skip, limit, status, agent_type)
    return AgentListResponse(
        agents=agents,
        total=total,
        page=skip // limit + 1,
        size=len(agents)
    )

@router.get("/agents/{agent_id}", response_model=Agent)
async def get_agent(
    agent_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get agent by ID"""
    service = AgentService(db)
    agent = await service.get_agent(agent_id, tenant_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.put("/agents/{agent_id}", response_model=Agent)
async def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(require_admin_or_member_role),
    db: Session = Depends(get_db)
):
    """Update agent"""
    service = AgentService(db)
    agent = await service.update_agent(agent_id, tenant_id, agent_data)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.delete("/agents/{agent_id}", status_code=204)
async def delete_agent(
    agent_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(require_admin_or_member_role),
    db: Session = Depends(get_db)
):
    """Delete (terminate) agent"""
    service = AgentService(db)
    success = await service.delete_agent(agent_id, tenant_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")

@router.post("/agents/{agent_id}/start", response_model=Agent)
async def start_agent(
    agent_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(require_admin_or_member_role),
    db: Session = Depends(get_db)
):
    """Start an agent"""
    service = AgentService(db)
    try:
        agent = await service.start_agent(agent_id, tenant_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return agent
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/agents/{agent_id}/stop", response_model=Agent)
async def stop_agent(
    agent_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(require_admin_or_member_role),
    db: Session = Depends(get_db)
):
    """Stop an agent"""
    service = AgentService(db)
    agent = await service.stop_agent(agent_id, tenant_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

# Task Endpoints
@router.post("/tasks", response_model=Task, status_code=201)
async def create_task(
    task_data: TaskCreate,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(require_admin_or_member_role),
    db: Session = Depends(get_db)
):
    """Create a new task"""
    service = TaskService(db)
    try:
        return await service.create_task(task_data, tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tasks", response_model=TaskListResponse)
async def get_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    agent_id: Optional[str] = None,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all tasks with filtering"""
    service = TaskService(db)
    tasks, total = await service.get_tasks(tenant_id, skip, limit, agent_id)
    return TaskListResponse(
        tasks=tasks,
        total=total,
        page=skip // limit + 1,
        size=len(tasks)
    )

@router.get("/tasks/{task_id}", response_model=Task)
async def get_task(
    task_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get task by ID"""
    service = TaskService(db)
    task = await service.get_task(task_id, tenant_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/tasks/{task_id}/execute", response_model=TaskExecution)
async def execute_task(
    task_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(require_admin_or_member_role),
    db: Session = Depends(get_db)
):
    """Execute a task"""
    service = TaskService(db)
    try:
        return await service.execute_task(task_id, tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Agent Tasks
@router.get("/agents/{agent_id}/tasks", response_model=TaskListResponse)
async def get_agent_tasks(
    agent_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all tasks for a specific agent"""
    # Verify agent exists within tenant
    agent_service = AgentService(db)
    agent = await agent_service.get_agent(agent_id, tenant_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Get tasks
    task_service = TaskService(db)
    tasks, total = await task_service.get_tasks(tenant_id, skip, limit, agent_id)
    return TaskListResponse(
        tasks=tasks,
        total=total,
        page=skip // limit + 1,
        size=len(tasks)
    )

# Chat Endpoints
@router.post("/agents/{agent_id}/chat", response_model=ChatResponse)
async def chat_with_agent(
    agent_id: str,
    chat_request: ChatRequest,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chat with an agent"""
    from app.services.chat_service import ChatService
    
    service = ChatService(db)
    return await service.chat_with_agent(
        agent_id=agent_id,
        message=chat_request.message,
        user_id=str(current_user.id),
        tenant_id=tenant_id
    )

@router.get("/agents/{agent_id}/chat/history")
async def get_chat_history(
    agent_id: str,
    limit: int = Query(50, ge=1, le=100),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat history with an agent"""
    from app.services.chat_service import ChatService
    
    service = ChatService(db)
    messages = await service.get_chat_history(
        agent_id=agent_id,
        user_id=str(current_user.id),
        tenant_id=tenant_id,
        limit=limit
    )
    return {"messages": messages}

@router.get("/agents/available/{agent_id}")
async def get_available_agents_for_connection(
    agent_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available agents for connection (excluding self)"""
    service = AgentService(db)
    agents = await service.get_available_agents_for_connection(agent_id, tenant_id)
    return {"agents": agents}