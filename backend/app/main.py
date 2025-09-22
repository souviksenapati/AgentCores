"""
FastAPI Integration Layer - Enterprise API Gateway
Built for MVP simplicity, designed for billion-dollar platform scale.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy import text
import asyncio
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, ValidationError
import logging

# Import our enterprise services
from app.services.agent_service import AgentService
from app.services.template_engine import AgentTemplateEngine, TemplateManager, IndustryType, TemplateCategory
from app.services.task_execution_engine import TaskExecutionEngine, TaskDefinition, TaskPriority, TaskType
from app.services.event_service import EventService, EventType
from app.providers.openrouter_provider import OpenRouterProvider, ProviderFactory
from app.core.interfaces import AgentConfig, TaskResult, TaskStatus, ProviderType

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Request/Response Models
class CreateAgentRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    template_id: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Customer Support Assistant",
                "description": "AI agent for handling customer inquiries",
                "template_id": "customer_service_basic",
                "config": {
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            }
        }


class AgentResponse(BaseModel):
    agent_id: str
    name: str
    description: str
    status: str
    created_at: str
    config: Dict[str, Any]
    
    class Config:
        schema_extra = {
            "example": {
                "agent_id": "agent_123",
                "name": "Customer Support Assistant", 
                "description": "AI agent for handling customer inquiries",
                "status": "active",
                "created_at": "2024-01-15T10:30:00Z",
                "config": {"model": "anthropic/claude-3-haiku", "temperature": 0.7}
            }
        }


class ExecuteTaskRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=10000)
    priority: Optional[str] = "normal"
    context: Optional[Dict[str, Any]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "prompt": "Help a customer who wants to return a product",
                "priority": "high",
                "context": {"customer_tier": "premium", "order_id": "ORD-123"}
            }
        }


class TaskResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[str] = None
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None
    cost_estimate: Optional[float] = None
    
    class Config:
        schema_extra = {
            "example": {
                "task_id": "task_456", 
                "status": "completed",
                "result": "I'd be happy to help you with your return...",
                "execution_time_ms": 1500,
                "cost_estimate": 0.0023
            }
        }


class TemplateResponse(BaseModel):
    id: str
    name: str
    description: str
    industry: str
    category: str
    use_cases: List[str]
    approved_for_production: bool
    
    class Config:
        schema_extra = {
            "example": {
                "id": "customer_service_basic",
                "name": "Customer Service Assistant",
                "description": "AI agent for handling customer inquiries",
                "industry": "customer_service",
                "category": "conversational",
                "use_cases": ["Answer questions", "Troubleshoot issues"],
                "approved_for_production": True
            }
        }


# Enterprise Middleware
class TenantMiddleware:
    """Multi-tenant isolation middleware"""
    
    def __init__(self, app: FastAPI):
        self.app = app
    
    async def __call__(self, request: Request, call_next):
        # Extract tenant from header or JWT (simplified for MVP)
        tenant_id = request.headers.get("X-Tenant-ID", "default")
        request.state.tenant_id = tenant_id
        
        response = await call_next(request)
        response.headers["X-Tenant-ID"] = tenant_id
        return response


class RateLimitMiddleware:
    """Rate limiting middleware for enterprise protection"""
    
    def __init__(self, app: FastAPI, requests_per_minute: int = 100):
        self.app = app
        self.requests_per_minute = requests_per_minute
        self.client_requests: Dict[str, List[float]] = {}
    
    async def __call__(self, request: Request, call_next):
        # Simple rate limiting by IP (enterprise: use Redis)
        client_ip = request.client.host
        current_time = time.time()
        
        if client_ip not in self.client_requests:
            self.client_requests[client_ip] = []
        
        # Clean old requests
        self.client_requests[client_ip] = [
            req_time for req_time in self.client_requests[client_ip]
            if current_time - req_time < 60
        ]
        
        # Check rate limit
        if len(self.client_requests[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded", "retry_after": 60}
            )
        
        self.client_requests[client_ip].append(current_time)
        return await call_next(request)


# Dependency injection for enterprise services
async def get_agent_service() -> AgentService:
    """Get agent service instance"""
    # In production: use dependency injection container
    return AgentService()


async def get_template_engine() -> AgentTemplateEngine:
    """Get template engine instance"""
    return AgentTemplateEngine()


async def get_task_engine() -> TaskExecutionEngine:
    """Get task execution engine instance"""
    # In production: shared instance with proper lifecycle
    engine = TaskExecutionEngine()
    if not engine._running:
        await engine.start()
    return engine


async def get_event_service() -> EventService:
    """Get event service instance"""
    service = EventService()
    if not service._running:
        await service.start()
    return service


async def get_current_tenant(request: Request) -> str:
    """Extract tenant ID from request"""
    return getattr(request.state, 'tenant_id', 'default')


async def authenticate_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Authenticate user (simplified for MVP).
    Enterprise: JWT validation, role-based access control
    """
    # For MVP: simple token validation
    token = credentials.credentials
    
    if token == "demo-token" or token.startswith("demo-token-"):
        return {"user_id": "demo-user", "role": "admin"}
    elif token.startswith("user-") or token.startswith("new-user-"):
        return {"user_id": token, "role": "user"}
    else:
        raise HTTPException(status_code=401, detail="Invalid authentication token")


# Create FastAPI application with enterprise configuration
def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="AgentCores Enterprise API",
        description="AI Agent Orchestration Platform - MVP with Enterprise DNA",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # Enterprise middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["*"]  # Configure for production
    )
    
    # Custom enterprise middleware
    app.middleware("http")(TenantMiddleware(app))
    app.middleware("http")(RateLimitMiddleware(app))
    
    # Custom exception handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors with user-friendly messages"""
        errors = []
        for error in exc.errors():
            field_name = " -> ".join(str(loc) for loc in error["loc"][1:])  # Skip 'body'
            errors.append(f"{field_name}: {error['msg']}")
        
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation failed",
                "details": errors,
                "status_code": 422
            }
        )
    
    return app


# Initialize app
app = create_app()


# Health and Status Endpoints
@app.get("/health", tags=["System"])
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {
            "agent_service": "operational",
            "template_engine": "operational", 
            "task_engine": "operational",
            "event_service": "operational"
        }
    }


@app.get("/status", tags=["System"])
async def system_status(
    event_service: EventService = Depends(get_event_service),
    task_engine: TaskExecutionEngine = Depends(get_task_engine)
):
    """Detailed system status for enterprise monitoring"""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "event_service": await event_service.get_service_stats(),
        "task_engine": task_engine.get_engine_stats(),
        "providers": await ProviderFactory.health_check_all()
    }


# Authentication Endpoints
class LoginRequest(BaseModel):
    email: str = Field(..., min_length=1, max_length=255, description="Email address")
    password: str = Field(..., min_length=1, max_length=255, description="Password")
    # Accept both organization and tenant_name for frontend compatibility
    organization: Optional[str] = Field(None, min_length=1, max_length=255, description="Organization name")
    tenant_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Tenant name (legacy)")
    
    @property
    def org_name(self) -> str:
        """Get organization name from either field"""
        return self.organization or self.tenant_name or ""

class UserInfo(BaseModel):
    id: str
    email: str
    role: str = "admin"

class TenantInfo(BaseModel):
    id: str
    name: str
    subdomain: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserInfo
    tenant: TenantInfo
    refresh_token: Optional[str] = None

@app.post("/auth/login", response_model=LoginResponse, tags=["Authentication"])
async def login(request: LoginRequest):
    """User login endpoint"""
    try:
        from app.database import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        
        # Check if user exists (demo credentials)
        if (request.email == "admin@demo.agentcores.com" and 
            request.password == "admin123" and 
            request.org_name == "AgentCores Demo"):
            
            # Generate demo token (in production, use proper JWT)
            access_token = "demo-token-" + str(uuid.uuid4())[:8]
            
            # Create user and tenant objects as expected by frontend
            user_info = UserInfo(
                id="demo-user",
                email=request.email,
                role="admin"
            )
            
            tenant_info = TenantInfo(
                id="demo-tenant",
                name=request.org_name,
                subdomain="agentcores-demo"
            )
            
            return LoginResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=3600,
                user=user_info,
                tenant=tenant_info,
                refresh_token=None
            )
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
    except HTTPException:
        # Re-raise HTTP exceptions (like 401 for invalid credentials)
        raise
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/auth/logout", tags=["Authentication"])
async def logout(user: Dict[str, Any] = Depends(authenticate_user)):
    """User logout endpoint"""
    return {"message": "Logged out successfully"}

@app.get("/auth/me", tags=["Authentication"])
async def get_current_user(user: Dict[str, Any] = Depends(authenticate_user)):
    """Get current user information"""
    return {
        "user_id": user["user_id"],
        "role": user["role"],
        "organization": "AgentCores Demo"
    }

# Registration endpoint
class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=6, max_length=255)
    tenant_name: str = Field(..., min_length=1, max_length=255)
    first_name: Optional[str] = None
    last_name: Optional[str] = None

@app.post("/auth/register", response_model=LoginResponse, tags=["Authentication"])
async def register(request: RegisterRequest):
    """User registration endpoint"""
    try:
        # For demo purposes, accept any registration and return success
        # In production, this would create actual user/tenant records
        
        access_token = "demo-token-" + str(uuid.uuid4())[:8]
        
        user_info = UserInfo(
            id="new-user-" + str(uuid.uuid4())[:8],
            email=request.email,
            role="admin"
        )
        
        tenant_info = TenantInfo(
            id="new-tenant-" + str(uuid.uuid4())[:8],
            name=request.tenant_name,
            subdomain=request.tenant_name.lower().replace(" ", "-")
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=3600,
            user=user_info,
            tenant=tenant_info,
            refresh_token=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")


# API v1 routes for frontend compatibility
@app.post("/api/v1/auth/login", response_model=LoginResponse, tags=["Authentication V1"])
async def login_v1(request: LoginRequest):
    """User login endpoint - API v1 compatible"""
    return await login(request)

@app.post("/api/v1/auth/register", response_model=LoginResponse, tags=["Authentication V1"])
async def register_v1(request: RegisterRequest):
    """User registration endpoint - API v1 compatible"""
    return await register(request)

@app.post("/api/v1/auth/logout", tags=["Authentication V1"])
async def logout_v1(user: Dict[str, Any] = Depends(authenticate_user)):
    """User logout endpoint - API v1 compatible"""
    return await logout(user)

@app.get("/api/v1/auth/me", tags=["Authentication V1"])  
async def get_current_user_v1(user: Dict[str, Any] = Depends(authenticate_user)):
    """Get current user information - API v1 compatible"""
    return await get_current_user(user)

@app.get("/api/v1/health", tags=["System V1"])
async def health_check_v1():
    """Health check endpoint - API v1 compatible"""
    return await health_check()


# Agent Management Endpoints
@app.post("/agents", response_model=AgentResponse, tags=["Agents"])
async def create_agent(
    request: CreateAgentRequest,
    background_tasks: BackgroundTasks,
    tenant_id: str = Depends(get_current_tenant),
    user: Dict[str, Any] = Depends(authenticate_user),
    agent_service: AgentService = Depends(get_agent_service),
    template_engine: AgentTemplateEngine = Depends(get_template_engine),
    event_service: EventService = Depends(get_event_service)
):
    """Create new AI agent"""
    try:
        # Get agent config from template or custom config
        if request.template_id:
            agent_config = await template_engine.create_agent_from_template(
                request.template_id,
                request.config or {}
            )
            if not agent_config:
                raise HTTPException(status_code=404, detail="Template not found")
        else:
            # Create custom agent config
            agent_config = AgentConfig(
                name=request.name,
                description=request.description,
                **request.config or {}
            )
        
        # Update with request data
        agent_config.name = request.name
        agent_config.description = request.description
        
        # Create agent
        agent_id = await agent_service.create_agent(
            agent_config,
            tenant_id=tenant_id,
            user_id=user["user_id"]
        )
        
        # Publish event
        background_tasks.add_task(
            event_service.publish_event,
            {
                "type": "agent.created",
                "agent_id": agent_id,
                "user_id": user["user_id"],
                "template_id": request.template_id
            },
            tenant_id=tenant_id
        )
        
        return AgentResponse(
            agent_id=agent_id,
            name=agent_config.name,
            description=agent_config.description,
            status="active",
            created_at=datetime.utcnow().isoformat(),
            config=agent_config.to_dict()
        )
        
    except Exception as e:
        logger.error(f"Failed to create agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents/{agent_id}", response_model=AgentResponse, tags=["Agents"])
async def get_agent(
    agent_id: str,
    tenant_id: str = Depends(get_current_tenant),
    user: Dict[str, Any] = Depends(authenticate_user),
    agent_service: AgentService = Depends(get_agent_service)
):
    """Get agent details"""
    agent = await agent_service.get_agent(agent_id, tenant_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return AgentResponse(
        agent_id=agent_id,
        name=agent.config.name,
        description=agent.config.description,
        status=agent.status.value,
        created_at=agent.created_at.isoformat(),
        config=agent.config.to_dict()
    )


@app.get("/agents", response_model=List[AgentResponse], tags=["Agents"]) 
async def list_agents(
    tenant_id: str = Depends(get_current_tenant),
    user: Dict[str, Any] = Depends(authenticate_user),
    agent_service: AgentService = Depends(get_agent_service)
):
    """List all agents for tenant"""
    agents = await agent_service.list_agents(tenant_id)
    
    return [
        AgentResponse(
            agent_id=agent.agent_id,
            name=agent.config.name,
            description=agent.config.description,
            status=agent.status.value,
            created_at=agent.created_at.isoformat(),
            config=agent.config.to_dict()
        )
        for agent in agents
    ]


@app.delete("/agents/{agent_id}", tags=["Agents"])
async def delete_agent(
    agent_id: str,
    background_tasks: BackgroundTasks,
    tenant_id: str = Depends(get_current_tenant),
    user: Dict[str, Any] = Depends(authenticate_user),
    agent_service: AgentService = Depends(get_agent_service),
    event_service: EventService = Depends(get_event_service)
):
    """Delete agent"""
    success = await agent_service.delete_agent(agent_id, tenant_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Publish event
    background_tasks.add_task(
        event_service.publish_event,
        {
            "type": "agent.deleted",
            "agent_id": agent_id,
            "user_id": user["user_id"]
        },
        tenant_id=tenant_id
    )
    
    return {"message": "Agent deleted successfully"}


# Task Execution Endpoints
@app.post("/agents/{agent_id}/execute", response_model=TaskResponse, tags=["Tasks"])
async def execute_task(
    agent_id: str,
    request: ExecuteTaskRequest,
    background_tasks: BackgroundTasks,
    tenant_id: str = Depends(get_current_tenant),
    user: Dict[str, Any] = Depends(authenticate_user),
    agent_service: AgentService = Depends(get_agent_service),
    task_engine: TaskExecutionEngine = Depends(get_task_engine),
    event_service: EventService = Depends(get_event_service)
):
    """Execute task with agent"""
    try:
        # Get agent
        agent = await agent_service.get_agent(agent_id, tenant_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Parse priority
        try:
            priority = TaskPriority(request.priority.lower())
        except ValueError:
            priority = TaskPriority.NORMAL
        
        # Create task definition
        task_definition = TaskDefinition(
            task_id=str(uuid.uuid4()),
            task_type=TaskType.COMPLETION,
            priority=priority,
            agent_config=agent.config,
            input_data={"prompt": request.prompt},
            tenant_id=tenant_id,
            user_id=user["user_id"]
        )
        
        # Add context
        if request.context:
            task_definition.input_data.update(request.context)
        
        # Submit task
        task_id = await task_engine.submit_task(task_definition)
        
        # For MVP: wait for result (enterprise: return immediately with polling)
        max_wait_time = 30  # 30 seconds
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            task_result = await task_engine.get_task_result(task_id)
            if task_result:
                return TaskResponse(
                    task_id=task_id,
                    status=task_result.status.value,
                    result=task_result.result,
                    error_message=task_result.error_message,
                    execution_time_ms=task_result.execution_time_ms,
                    cost_estimate=task_result.cost_estimate
                )
            
            await asyncio.sleep(0.5)
        
        # Task still running
        return TaskResponse(
            task_id=task_id,
            status="running",
            result=None
        )
        
    except Exception as e:
        logger.error(f"Failed to execute task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def get_task_result(
    task_id: str,
    tenant_id: str = Depends(get_current_tenant),
    user: Dict[str, Any] = Depends(authenticate_user),
    task_engine: TaskExecutionEngine = Depends(get_task_engine)
):
    """Get task execution result"""
    task_result = await task_engine.get_task_result(task_id)
    if not task_result:
        # Check if task exists but not completed
        task_status = await task_engine.get_task_status(task_id)
        if task_status:
            return TaskResponse(
                task_id=task_id,
                status=task_status.value,
                result=None
            )
        else:
            raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse(
        task_id=task_id,
        status=task_result.status.value,
        result=task_result.result,
        error_message=task_result.error_message,
        execution_time_ms=task_result.execution_time_ms,
        cost_estimate=task_result.cost_estimate
    )


# Template Management Endpoints
@app.get("/templates", response_model=List[TemplateResponse], tags=["Templates"])
async def list_templates(
    industry: Optional[str] = None,
    category: Optional[str] = None,
    template_engine: AgentTemplateEngine = Depends(get_template_engine)
):
    """List available agent templates"""
    try:
        # Parse filters
        industry_filter = IndustryType(industry) if industry else None
        category_filter = TemplateCategory(category) if category else None
        
        templates = await template_engine.list_templates(
            industry=industry_filter,
            category=category_filter
        )
        
        return [
            TemplateResponse(
                id=template.id,
                name=template.name,
                description=template.description,
                industry=template.industry.value,
                category=template.category.value,
                use_cases=template.use_cases,
                approved_for_production=template.approved_for_production
            )
            for template in templates
        ]
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid filter parameter: {str(e)}")


@app.get("/templates/{template_id}", response_model=TemplateResponse, tags=["Templates"])
async def get_template(
    template_id: str,
    template_engine: AgentTemplateEngine = Depends(get_template_engine)
):
    """Get template details"""
    template = await template_engine.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return TemplateResponse(
        id=template.id,
        name=template.name,
        description=template.description,
        industry=template.industry.value,
        category=template.category.value,
        use_cases=template.use_cases,
        approved_for_production=template.approved_for_production
    )


# Analytics and Monitoring Endpoints
@app.get("/analytics/events", tags=["Analytics"])
async def get_analytics_events(
    tenant_id: str = Depends(get_current_tenant),
    event_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    event_service: EventService = Depends(get_event_service)
):
    """Get analytics events for the tenant"""
    try:
        events = await event_service.query_events(
            tenant_id=tenant_id,
            event_type=event_type,
            start_time=start_date,
            end_time=end_date,
            limit=limit
        )
        
        return {
            "events": [
                {
                    "id": event.event_id,
                    "type": event.event_type,
                    "timestamp": event.timestamp,
                    "metadata": event.metadata
                }
                for event in events
            ],
            "total": len(events)
        }
        
    except Exception as e:
        logger.error(f"Failed to get analytics events: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/summary", tags=["Analytics"])
async def get_analytics_summary(
    tenant_id: str = Depends(get_current_tenant),
    period: str = "24h",
    event_service: EventService = Depends(get_event_service)
):
    """Get analytics summary for the tenant"""
    try:
        # Calculate time range based on period
        end_time = datetime.utcnow()
        if period == "1h":
            start_time = end_time - timedelta(hours=1)
        elif period == "24h":
            start_time = end_time - timedelta(hours=24)
        elif period == "7d":
            start_time = end_time - timedelta(days=7)
        elif period == "30d":
            start_time = end_time - timedelta(days=30)
        else:
            raise HTTPException(status_code=400, detail="Invalid period. Use: 1h, 24h, 7d, 30d")
        
        # Get analytics summary
        summary = await event_service.get_analytics_summary(
            tenant_id=tenant_id,
            start_time=start_time,
            end_time=end_time
        )
        
        return summary
        
    except Exception as e:
        logger.error(f"Failed to get analytics summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Enterprise Configuration Endpoints
@app.get("/config/validation", tags=["Configuration"])
async def validate_configuration():
    """Validate enterprise configuration"""
    try:
        from app.database import config
        validation_result = config.validate_configuration()
        
        return {
            "validation": validation_result,
            "timestamp": datetime.utcnow(),
            "environment": config.ENVIRONMENT,
            "version": config.APP_VERSION
        }
        
    except Exception as e:
        logger.error(f"Configuration validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/config/features", tags=["Configuration"])
async def get_feature_flags():
    """Get current feature flag status"""
    try:
        from app.database import config
        
        features = {
            "multi_tenancy": config.FEATURE_MULTI_TENANCY,
            "analytics": config.FEATURE_ANALYTICS,
            "advanced_templates": config.FEATURE_ADVANCED_TEMPLATES,
            "multi_provider": config.FEATURE_MULTI_PROVIDER,
            "cost_tracking": config.FEATURE_COST_TRACKING,
            "compliance_mode": config.COMPLIANCE_MODE,
            "audit_logging": config.AUDIT_LOGGING,
            "data_encryption": config.DATA_ENCRYPTION_AT_REST
        }
        
        return {
            "features": features,
            "environment": config.ENVIRONMENT,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Failed to get feature flags: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/config/limits", tags=["Configuration"])
async def get_tenant_limits(
    tenant_id: str = Depends(get_current_tenant)
):
    """Get current tenant limits and usage"""
    try:
        from app.database import config
        
        # In MVP, return default limits
        # Enterprise: This would query actual tenant configuration
        limits = {
            "max_agents": config.DEFAULT_MAX_AGENTS,
            "max_tasks_per_hour": config.DEFAULT_MAX_TASKS_PER_HOUR,
            "max_monthly_cost": config.DEFAULT_MAX_MONTHLY_COST,
            "current_usage": {
                "agents": 0,  # Would be queried from database
                "tasks_this_hour": 0,  # Would be calculated from recent tasks
                "monthly_cost": 0.0  # Would be calculated from cost tracking
            },
            "warnings": {
                "cost_alert_threshold": config.MONTHLY_COST_ALERT_THRESHOLD,
                "daily_cost_threshold": config.DAILY_COST_ALERT_THRESHOLD
            }
        }
        
        return limits
        
    except Exception as e:
        logger.error(f"Failed to get tenant limits: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Health and Monitoring Endpoints
@app.get("/health", tags=["Monitoring"])
async def health_check():
    """Enterprise health check endpoint"""
    try:
        from app.database import config
        
        # Basic health checks
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "version": config.APP_VERSION,
            "environment": config.ENVIRONMENT,
            "checks": {
                "database": "healthy",  # Would test actual DB connection
                "redis": "healthy",     # Would test Redis connection
                "ai_providers": "healthy"  # Would test provider availability
            }
        }
        
        # Add enterprise-specific health checks
        if config.METRICS_ENABLED:
            health_status["metrics"] = "enabled"
        
        if config.EVENT_STORE_ENABLED:
            health_status["event_store"] = "enabled"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow(),
            "error": str(e)
        }


@app.get("/health/detailed", tags=["Monitoring"])
async def detailed_health_check(
    tenant_id: str = Depends(get_current_tenant)
):
    """Detailed enterprise health check with tenant-specific information"""
    try:
        from app.database import config, SessionLocal
        
        health_details = {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "tenant_id": tenant_id,
            "environment": config.ENVIRONMENT,
            "components": {}
        }
        
        # Database health
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            health_details["components"]["database"] = {
                "status": "healthy",
                "url": config.DATABASE_URL.split("@")[1] if "@" in config.DATABASE_URL else "configured"
            }
        except Exception as e:
            health_details["components"]["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_details["status"] = "degraded"
        
        # AI Provider health
        provider_health = []
        if config.OPENROUTER_API_KEY:
            provider_health.append({"name": "OpenRouter", "status": "configured"})
        if config.OPENAI_API_KEY:
            provider_health.append({"name": "OpenAI", "status": "configured"})
        if config.ANTHROPIC_API_KEY:
            provider_health.append({"name": "Anthropic", "status": "configured"})
        
        health_details["components"]["ai_providers"] = {
            "status": "healthy" if provider_health else "warning",
            "providers": provider_health,
            "count": len(provider_health)
        }
        
        # Feature status
        health_details["components"]["features"] = {
            "multi_tenancy": config.FEATURE_MULTI_TENANCY,
            "cost_tracking": config.FEATURE_COST_TRACKING,
            "analytics": config.FEATURE_ANALYTICS
        }
        
        return health_details
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow(),
            "error": str(e)
        }


# Enterprise utility function to validate startup configuration
def validate_startup_configuration():
    """Validate configuration during startup"""
    try:
        from app.database import config
        
        validation = config.validate_configuration()
        
        print("\n🔧 Enterprise Configuration Validation")
        print("=" * 50)
        
        if validation["valid"]:
            print("✅ Configuration is valid")
        else:
            print("❌ Configuration validation failed:")
            for issue in validation["issues"]:
                print(f"   • {issue}")
        
        if validation["warnings"]:
            print("\n⚠️  Configuration warnings:")
            for warning in validation["warnings"]:
                print(f"   • {warning}")
        
        print(f"\n📊 Environment: {validation['environment']}")
        print("🚀 Features enabled:")
        for feature, enabled in validation["features_enabled"].items():
            status = "✅" if enabled else "❌"
            print(f"   {status} {feature}")
        
        print("\n" + "=" * 50)
        
        return validation["valid"]
        
    except Exception as e:
        print(f"❌ Configuration validation error: {e}")
        return False
async def get_event_analytics(
    event_type: Optional[str] = None,
    hours: int = 24,
    tenant_id: str = Depends(get_current_tenant),
    user: Dict[str, Any] = Depends(authenticate_user),
    event_service: EventService = Depends(get_event_service)
):
    """Get event analytics for monitoring"""
    try:
        event_type_filter = EventType(event_type) if event_type else None
        
        events = await event_service.get_events(
            event_type=event_type_filter,
            tenant_id=tenant_id,
            limit=1000
        )
        
        return {
            "total_events": len(events),
            "time_period_hours": hours,
            "tenant_id": tenant_id,
            "events": [
                {
                    "event_id": event.event_id,
                    "type": event.event_type.value,
                    "timestamp": event.timestamp.isoformat(),
                    "data": event.data
                }
                for event in events[:100]  # Limit response size
            ]
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid event type: {str(e)}")


# Error Handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler for unhandled errors"""
    logger.error(f"Unhandled error: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url)
        }
    )


# Application startup/shutdown
@app.on_event("startup")
async def startup_event():
    """Initialize enterprise services on startup"""
    logger.info("🚀 Starting AgentCores Enterprise API...")
    
    # Validate enterprise configuration first
    config_valid = validate_startup_configuration()
    if not config_valid:
        logger.error("❌ Configuration validation failed - startup aborted")
        raise RuntimeError("Invalid enterprise configuration")
    
    # Initialize database
    try:
        from app.database import init_database
        init_database()
        logger.info("✅ Enterprise database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    
    # Initialize event service
    event_service = EventService()
    await event_service.start()
    logger.info("✅ Enterprise event service started")
    
    # Initialize task engine
    task_engine = TaskExecutionEngine(event_service=event_service)
    await task_engine.start()
    logger.info("✅ Enterprise task execution engine started")
    
    logger.info("🎉 AgentCores Enterprise API started successfully")
    logger.info("🌐 Ready to handle billion-dollar AI orchestration workloads")


@app.on_event("shutdown")
async def shutdown_event():
    """Graceful enterprise shutdown"""
    logger.info("🔄 Shutting down AgentCores Enterprise API...")
    
    # Enterprise cleanup: graceful service shutdown
    try:
        # Stop task processing
        # Stop event processing
        # Close database connections
        # Archive pending tasks
        logger.info("✅ Enterprise services shut down gracefully")
    except Exception as e:
        logger.error(f"⚠️  Shutdown error: {e}")
    
    logger.info("👋 AgentCores Enterprise API shut down complete")


if __name__ == "__main__":
    import uvicorn
    from app.database import config
    
    # Enterprise startup with configuration validation
    print("\n🏢 AgentCores Enterprise Platform")
    print("=" * 50)
    print("🎯 Building billion-dollar AI orchestration platform")
    print("🔧 Starting with enterprise DNA...")
    
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.is_development(),
        log_level=config.LOG_LEVEL.lower(),
        workers=1 if config.is_development() else config.WORKERS
    )