from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
import asyncio
import httpx
import hashlib
import secrets
from jose import jwt, JWTError
from passlib.context import CryptContext
from loguru import logger

from app.models.database import Agent, Task, TaskExecution, AgentStatus, TaskStatus, User, Tenant, TenantInvitation, AuditLog, UserRole, TenantStatus, InvitationStatus
from app.schemas import AgentCreate, AgentUpdate, TaskCreate, TaskUpdate

class AgentService:
    def __init__(self, db: Session):
        self.db = db

    async def create_agent(self, agent_data: AgentCreate, tenant_id: str) -> Agent:
        """Create a new agent"""
        agent_dict = agent_data.model_dump()
        agent_dict["tenant_id"] = tenant_id
        
        db_agent = Agent(**agent_dict)
        self.db.add(db_agent)
        self.db.commit()
        self.db.refresh(db_agent)
        
        logger.info(f"Created agent {db_agent.id} of type {db_agent.agent_type} for tenant {tenant_id}")
        return db_agent

    async def get_agent(self, agent_id: str, tenant_id: str) -> Optional[Agent]:
        """Get agent by ID within tenant"""
        return self.db.query(Agent).filter(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id
        ).first()

    async def get_agents(
        self, 
        tenant_id: str,
        skip: int = 0, 
        limit: int = 100,
        status: Optional[AgentStatus] = None,
        agent_type: Optional[str] = None
    ) -> tuple[List[Agent], int]:
        """Get agents with filtering within tenant"""
        query = self.db.query(Agent).filter(Agent.tenant_id == tenant_id)
        
        if status:
            query = query.filter(Agent.status == status)
        if agent_type:
            query = query.filter(Agent.agent_type == agent_type)
            
        total = query.count()
        agents = query.offset(skip).limit(limit).all()
        
        return agents, total

    async def update_agent(self, agent_id: str, tenant_id: str, agent_data: AgentUpdate) -> Optional[Agent]:
        """Update agent within tenant"""
        db_agent = await self.get_agent(agent_id, tenant_id)
        if not db_agent:
            return None
            
        update_data = agent_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_agent, field, value)
            
        db_agent.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_agent)
        
        logger.info(f"Updated agent {agent_id} in tenant {tenant_id}")
        return db_agent

    async def delete_agent(self, agent_id: str, tenant_id: str) -> bool:
        """Delete agent within tenant"""
        db_agent = await self.get_agent(agent_id, tenant_id)
        if not db_agent:
            return False
            
        # Set status to terminated instead of hard delete
        db_agent.status = AgentStatus.TERMINATED
        db_agent.updated_at = datetime.utcnow()
        self.db.commit()
        
        logger.info(f"Terminated agent {agent_id} in tenant {tenant_id}")
        return True

    async def start_agent(self, agent_id: str, tenant_id: str) -> Optional[Agent]:
        """Start an agent within tenant"""
        db_agent = await self.get_agent(agent_id, tenant_id)
        if not db_agent:
            return None
            
        if db_agent.status not in [AgentStatus.IDLE, AgentStatus.PAUSED]:
            raise ValueError(f"Cannot start agent in {db_agent.status} status")
            
        db_agent.status = AgentStatus.RUNNING
        db_agent.last_active = datetime.utcnow()
        db_agent.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_agent)
        
        logger.info(f"Started agent {agent_id} in tenant {tenant_id}")
        return db_agent

    async def stop_agent(self, agent_id: str, tenant_id: str) -> Optional[Agent]:
        """Stop an agent within tenant"""
        db_agent = await self.get_agent(agent_id, tenant_id)
        if not db_agent:
            return None
            
        db_agent.status = AgentStatus.IDLE
        db_agent.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_agent)
        
        logger.info(f"Stopped agent {agent_id} in tenant {tenant_id}")
        return db_agent

class TaskService:
    def __init__(self, db: Session):
        self.db = db

    async def create_task(self, task_data: TaskCreate, tenant_id: str) -> Task:
        """Create a new task"""
        # Verify agent exists within tenant
        agent = self.db.query(Agent).filter(
            Agent.id == task_data.agent_id,
            Agent.tenant_id == tenant_id
        ).first()
        if not agent:
            raise ValueError(f"Agent {task_data.agent_id} not found in tenant {tenant_id}")
            
        task_dict = task_data.model_dump()
        task_dict["tenant_id"] = tenant_id
        
        db_task = Task(**task_dict)
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        
        logger.info(f"Created task {db_task.id} for agent {task_data.agent_id} in tenant {tenant_id}")
        return db_task

    async def get_task(self, task_id: str, tenant_id: str) -> Optional[Task]:
        """Get task by ID within tenant"""
        return self.db.query(Task).filter(
            Task.id == task_id,
            Task.tenant_id == tenant_id
        ).first()

    async def get_tasks(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        agent_id: Optional[str] = None
    ) -> tuple[List[Task], int]:
        """Get tasks with filtering within tenant"""
        query = self.db.query(Task).filter(Task.tenant_id == tenant_id)
        
        if agent_id:
            query = query.filter(Task.agent_id == agent_id)
            
        total = query.count()
        tasks = query.offset(skip).limit(limit).all()
        
        return tasks, total

    async def execute_task(self, task_id: str, tenant_id: str) -> TaskExecution:
        """Execute a task within tenant"""
        task = await self.get_task(task_id, tenant_id)
        if not task:
            raise ValueError(f"Task {task_id} not found in tenant {tenant_id}")
            
        agent = self.db.query(Agent).filter(
            Agent.id == task.agent_id,
            Agent.tenant_id == tenant_id
        ).first()
        if not agent:
            raise ValueError(f"Agent {task.agent_id} not found in tenant {tenant_id}")
            
        if agent.status != AgentStatus.RUNNING:
            raise ValueError(f"Agent {agent.id} is not running")

        # Create execution record
        execution = TaskExecution(
            agent_id=task.agent_id,
            task_id=task.id,
            tenant_id=tenant_id,
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
            logger.error(f"Task {task_id} failed in tenant {tenant_id}: {str(e)}")
            
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


# Authentication Configuration
SECRET_KEY = "your-secret-key-change-in-production"  # TODO: Move to environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def hash_password(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, data: dict) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None

    async def authenticate_user(self, email: str, password: str, tenant_name: str) -> Optional[User]:
        """Authenticate user with email, password, and tenant name"""
        # Get tenant by name (more user-friendly than subdomain)
        tenant = self.db.query(Tenant).filter(
            Tenant.name == tenant_name,
            Tenant.status.in_([TenantStatus.ACTIVE, TenantStatus.TRIAL])
        ).first()
        
        if not tenant:
            logger.warning(f"Authentication failed: Tenant '{tenant_name}' not found or inactive")
            return None

        # Get user within tenant
        user = self.db.query(User).filter(
            User.email == email,
            User.tenant_id == tenant.id,
            User.is_active == True
        ).first()

        if not user:
            logger.warning(f"Authentication failed: User {email} not found in tenant '{tenant_name}'")
            return None

        # Check if user is locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            logger.warning(f"Authentication failed: User {email} is locked until {user.locked_until}")
            return None

        # Verify password
        if not self.verify_password(password, user.password_hash):
            # Increment failed attempts
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=15)
            self.db.commit()
            
            logger.warning(f"Authentication failed: Invalid password for user {email}")
            return None

        # Successful login - reset failed attempts and update last login
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.utcnow()
        self.db.commit()

        # Log successful authentication
        await self._log_audit_event(
            tenant_id=tenant.id,
            user_id=user.id,
            action="LOGIN",
            resource_type="User",
            resource_id=user.id
        )

        logger.info(f"User {email} authenticated successfully in tenant '{tenant_name}'")
        return user

    async def register_user(self, email: str, password: str, first_name: str, last_name: str, tenant_id: str, role: UserRole = UserRole.MEMBER) -> User:
        """Register a new user"""
        # Check if user already exists in tenant
        existing_user = self.db.query(User).filter(
            User.email == email,
            User.tenant_id == tenant_id
        ).first()
        
        if existing_user:
            raise ValueError(f"User with email {email} already exists in this tenant")

        # Verify tenant exists and is active
        tenant = self.db.query(Tenant).filter(
            Tenant.id == tenant_id,
            Tenant.status.in_([TenantStatus.ACTIVE, TenantStatus.TRIAL])
        ).first()
        
        if not tenant:
            raise ValueError("Invalid or inactive tenant")

        # Check user limit
        user_count = self.db.query(User).filter(User.tenant_id == tenant_id).count()
        if user_count >= tenant.max_users:
            raise ValueError(f"Tenant has reached maximum user limit of {tenant.max_users}")

        # Create user
        user = User(
            email=email,
            password_hash=self.hash_password(password),
            first_name=first_name,
            last_name=last_name,
            role=role,
            tenant_id=tenant_id
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # Log user creation
        await self._log_audit_event(
            tenant_id=tenant_id,
            user_id=user.id,
            action="CREATE",
            resource_type="User",
            resource_id=user.id,
            new_values={"email": email, "role": role.value}
        )

        logger.info(f"User {email} registered in tenant {tenant_id}")
        return user

    async def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from JWT token"""
        payload = self.verify_token(token)
        if not payload:
            return None

        user_id = payload.get("sub")
        tenant_id = payload.get("tenant_id")
        
        if not user_id or not tenant_id:
            return None

        user = self.db.query(User).filter(
            User.id == user_id,
            User.tenant_id == tenant_id,
            User.is_active == True
        ).first()

        return user

    async def _log_audit_event(self, tenant_id: str, action: str, resource_type: str, resource_id: str = None, user_id: str = None, old_values: dict = None, new_values: dict = None, ip_address: str = None, user_agent: str = None):
        """Log audit event"""
        audit_log = AuditLog(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            tenant_id=tenant_id,
            user_id=user_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.db.add(audit_log)
        self.db.commit()


class TenantService:
    def __init__(self, db: Session):
        self.db = db

    async def create_tenant(self, name: str, contact_email: str, contact_name: str, subscription_tier: str = "free") -> Tenant:
        """Create a new tenant"""
        # Check if organization name is already taken
        existing_tenant = self.db.query(Tenant).filter(Tenant.name == name).first()
        if existing_tenant:
            raise ValueError(f"Organization name '{name}' is already taken")

        # Generate a unique subdomain based on the name (for backward compatibility)
        import re
        subdomain = re.sub(r'[^a-zA-Z0-9]+', '-', name.lower()).strip('-')
        subdomain = subdomain[:50]  # Limit length
        
        # Ensure subdomain uniqueness by appending number if needed
        base_subdomain = subdomain
        counter = 1
        while self.db.query(Tenant).filter(Tenant.subdomain == subdomain).first():
            subdomain = f"{base_subdomain}-{counter}"
            counter += 1

        # Set trial end date
        trial_end = datetime.utcnow() + timedelta(days=14)

        tenant = Tenant(
            name=name,
            subdomain=subdomain,  # Auto-generated for backward compatibility
            contact_email=contact_email,
            contact_name=contact_name,
            status=TenantStatus.TRIAL,
            subscription_tier=subscription_tier,
            trial_end=trial_end
        )
        
        self.db.add(tenant)
        self.db.commit()
        self.db.refresh(tenant)

        logger.info(f"Created tenant {name} with auto-generated subdomain {subdomain}")
        return tenant

    async def get_tenant_by_name(self, name: str) -> Optional[Tenant]:
        """Get tenant by name"""
        return self.db.query(Tenant).filter(Tenant.name == name).first()

    async def get_tenant_by_subdomain(self, subdomain: str) -> Optional[Tenant]:
        """Get tenant by subdomain (kept for backward compatibility)"""
        return self.db.query(Tenant).filter(Tenant.subdomain == subdomain).first()

    async def invite_user(self, tenant_id: str, email: str, role: UserRole, invited_by_user_id: str) -> TenantInvitation:
        """Create user invitation"""
        # Check if user already exists in tenant
        existing_user = self.db.query(User).filter(
            User.email == email,
            User.tenant_id == tenant_id
        ).first()
        
        if existing_user:
            raise ValueError(f"User with email {email} already exists in this tenant")

        # Check if invitation already exists
        existing_invitation = self.db.query(TenantInvitation).filter(
            TenantInvitation.email == email,
            TenantInvitation.tenant_id == tenant_id,
            TenantInvitation.status == InvitationStatus.PENDING
        ).first()
        
        if existing_invitation:
            raise ValueError(f"Pending invitation already exists for {email}")

        # Generate secure token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=7)

        invitation = TenantInvitation(
            email=email,
            role=role,
            tenant_id=tenant_id,
            invited_by_user_id=invited_by_user_id,
            token=token,
            expires_at=expires_at
        )
        
        self.db.add(invitation)
        self.db.commit()
        self.db.refresh(invitation)

        logger.info(f"Created invitation for {email} to tenant {tenant_id}")
        return invitation

    async def accept_invitation(self, token: str, password: str, first_name: str, last_name: str) -> User:
        """Accept user invitation and create account"""
        invitation = self.db.query(TenantInvitation).filter(
            TenantInvitation.token == token,
            TenantInvitation.status == InvitationStatus.PENDING
        ).first()
        
        if not invitation:
            raise ValueError("Invalid or expired invitation")

        if invitation.expires_at < datetime.utcnow():
            invitation.status = InvitationStatus.EXPIRED
            self.db.commit()
            raise ValueError("Invitation has expired")

        # Create user account
        auth_service = AuthService(self.db)
        user = await auth_service.register_user(
            email=invitation.email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            tenant_id=invitation.tenant_id,
            role=invitation.role
        )

        # Mark invitation as accepted
        invitation.status = InvitationStatus.ACCEPTED
        invitation.accepted_at = datetime.utcnow()
        self.db.commit()

        logger.info(f"User {invitation.email} accepted invitation and joined tenant {invitation.tenant_id}")
        return user