from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas import (
    Agent, AgentCreate, AgentUpdate, AgentListResponse,
    Task, TaskCreate, TaskUpdate, TaskListResponse,
    TaskExecution, TaskExecutionResponse,
    AgentStatus, TaskStatus
)
from app.services.agent_service import AgentService, TaskService

router = APIRouter()

# Agent Endpoints
@router.post("/agents", response_model=Agent, status_code=201)
async def create_agent(
    agent_data: AgentCreate,
    db: Session = Depends(get_db)
):
    """Create a new agent"""
    service = AgentService(db)
    return await service.create_agent(agent_data)

@router.get("/agents", response_model=AgentListResponse)
async def get_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[AgentStatus] = None,
    agent_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all agents with filtering"""
    service = AgentService(db)
    agents, total = await service.get_agents(skip, limit, status, agent_type)
    return AgentListResponse(
        agents=agents,
        total=total,
        page=skip // limit + 1,
        size=len(agents)
    )

@router.get("/agents/{agent_id}", response_model=Agent)
async def get_agent(
    agent_id: str,
    db: Session = Depends(get_db)
):
    """Get agent by ID"""
    service = AgentService(db)
    agent = await service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.put("/agents/{agent_id}", response_model=Agent)
async def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    db: Session = Depends(get_db)
):
    """Update agent"""
    service = AgentService(db)
    agent = await service.update_agent(agent_id, agent_data)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.delete("/agents/{agent_id}", status_code=204)
async def delete_agent(
    agent_id: str,
    db: Session = Depends(get_db)
):
    """Delete (terminate) agent"""
    service = AgentService(db)
    success = await service.delete_agent(agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")

@router.post("/agents/{agent_id}/start", response_model=Agent)
async def start_agent(
    agent_id: str,
    db: Session = Depends(get_db)
):
    """Start an agent"""
    service = AgentService(db)
    try:
        agent = await service.start_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return agent
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/agents/{agent_id}/stop", response_model=Agent)
async def stop_agent(
    agent_id: str,
    db: Session = Depends(get_db)
):
    """Stop an agent"""
    service = AgentService(db)
    agent = await service.stop_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

# Task Endpoints
@router.post("/tasks", response_model=Task, status_code=201)
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db)
):
    """Create a new task"""
    service = TaskService(db)
    try:
        return await service.create_task(task_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tasks", response_model=TaskListResponse)
async def get_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    agent_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all tasks with filtering"""
    service = TaskService(db)
    tasks, total = await service.get_tasks(skip, limit, agent_id)
    return TaskListResponse(
        tasks=tasks,
        total=total,
        page=skip // limit + 1,
        size=len(tasks)
    )

@router.get("/tasks/{task_id}", response_model=Task)
async def get_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """Get task by ID"""
    service = TaskService(db)
    task = await service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/tasks/{task_id}/execute", response_model=TaskExecution)
async def execute_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """Execute a task"""
    service = TaskService(db)
    try:
        return await service.execute_task(task_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Agent Tasks
@router.get("/agents/{agent_id}/tasks", response_model=TaskListResponse)
async def get_agent_tasks(
    agent_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all tasks for a specific agent"""
    # Verify agent exists
    agent_service = AgentService(db)
    agent = await agent_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Get tasks
    task_service = TaskService(db)
    tasks, total = await task_service.get_tasks(skip, limit, agent_id)
    return TaskListResponse(
        tasks=tasks,
        total=total,
        page=skip // limit + 1,
        size=len(tasks)
    )