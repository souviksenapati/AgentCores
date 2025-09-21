# AgentCores - Multi-Tenant AI Agent Management Platform

🚀 **Enterprise-Scale AI Agent Management** - Built with Python/FastAPI backend and React frontend

## 🏗️ Architecture Overview

AgentCores is a next-generation multi-tenant AI agent management platform designed for enterprise SaaS deployment. This version provides comprehensive agent lifecycle management with full tenant isolation, user authentication, and role-based access control.

### Core Components:
- **Backend API**: FastAPI with PostgreSQL and JWT Authentication
- **Frontend Dashboard**: React with Material-UI and Multi-Tenant Support
- **Database**: PostgreSQL with complete tenant isolation
- **Authentication**: JWT with refresh tokens and role-based access
- **Containerization**: Docker Compose for easy deployment

## 🌟 Multi-Tenant Features

### 🏢 Organization Management
- **Complete Tenant Isolation**: Each organization has isolated data
- **Subscription Tiers**: Free, Basic, Professional, Enterprise
- **Custom Subdomains**: Each tenant gets their own subdomain
- **Resource Limits**: Per-tier agent and task limits

### � User Management
- **Role-Based Access Control**: Owner, Admin, Member roles
- **User Invitations**: Invite team members to organizations
- **Profile Management**: User profiles and preferences
- **Audit Logging**: Track all user actions

### 🔐 Enterprise Security
- **JWT Authentication**: Secure token-based authentication
- **Refresh Tokens**: Automatic token renewal
- **Password Security**: Bcrypt hashing with salt
- **Session Management**: Secure session handling

## �🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for local development)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd AgentCores
cp backend/.env.example backend/.env
```

### 2. Run with Docker (Recommended)
```bash
# Start all services (optimized with hot reload)
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### 3. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 4. Getting Started
1. **Create Organization**: Visit http://localhost:3000/create-tenant
2. **Register Admin User**: Create your organization admin account
3. **Setup Team**: Invite users to your organization
4. **Create Agents**: Start building your AI agent workflow

## � Authentication Flow

### New Organization Setup
1. **Create Tenant**: Organization details and subdomain
2. **Admin Registration**: First user becomes organization owner
3. **Team Building**: Invite users with different roles
4. **Agent Management**: Create and manage AI agents

### User Roles
- **Owner**: Full organization control, billing, user management
- **Admin**: User management, agent configuration
- **Member**: Agent usage, task creation

## 📊 Database Schema (Multi-Tenant)

### Tenants Table
```sql
- id (UUID, Primary Key)
- name (String, Organization name)
- subdomain (String, Unique subdomain)
- subscription_tier (Enum: free, basic, professional, enterprise)
- contact_email, contact_name (String)
- settings (JSON)
- created_at, updated_at (Timestamps)
```

### Users Table
```sql
- id (UUID, Primary Key)
- tenant_id (UUID, Foreign Key)
- email (String, Unique per tenant)
- full_name (String)
- hashed_password (String)
- role (Enum: owner, admin, member)
- is_active (Boolean)
- last_login (Timestamp)
- created_at, updated_at (Timestamps)
```

### Agents Table (Tenant-Scoped)
```sql
- id (UUID, Primary Key)
- tenant_id (UUID, Foreign Key)
- created_by (UUID, Foreign Key to Users)
- name (String, Required)
- description (Text)
- agent_type (String: gpt-4, claude, custom)
- status (Enum: idle, running, paused, error, terminated)
- configuration (JSON)
- capabilities (JSON Array)
- created_at, updated_at (Timestamps)
```

### Tasks Table (Tenant-Scoped)
```sql
- id (UUID, Primary Key)
- tenant_id (UUID, Foreign Key)
- created_by (UUID, Foreign Key to Users)
- agent_id (UUID, Foreign Key)
- name (String, Required)
- task_type (String)
- input_data (JSON)
- priority (Integer 1-5)
- status (Enum: pending, running, completed, failed)
- created_at, updated_at (Timestamps)
```

### Additional Multi-Tenant Tables
- **tenant_invitations**: User invitation management
- **audit_logs**: Complete action tracking
- **tenant_settings**: Organization preferences
- **billing_info**: Subscription and usage tracking

## 🎯 API Endpoints

### Authentication & Tenant Management
```bash
# Create new organization
POST /api/v1/tenants

# User registration
POST /api/v1/auth/register

# User login
POST /api/v1/auth/login

# Refresh token
POST /api/v1/auth/refresh

# User profile
GET /api/v1/auth/me
PUT /api/v1/auth/profile

# Tenant user management
GET /api/v1/tenants/users
POST /api/v1/tenants/users/invite
PUT /api/v1/tenants/users/{user_id}
DELETE /api/v1/tenants/users/{user_id}
```

### Agent Management (Tenant-Scoped)
```bash
# All endpoints automatically scoped to user's tenant
GET /api/v1/agents
POST /api/v1/agents
GET /api/v1/agents/{agent_id}
PUT /api/v1/agents/{agent_id}
DELETE /api/v1/agents/{agent_id}
POST /api/v1/agents/{agent_id}/start
POST /api/v1/agents/{agent_id}/stop
```

### Task Management (Tenant-Scoped)
```bash
# All endpoints automatically scoped to user's tenant
GET /api/v1/tasks
POST /api/v1/tasks
GET /api/v1/tasks/{task_id}
PUT /api/v1/tasks/{task_id}
DELETE /api/v1/tasks/{task_id}
POST /api/v1/tasks/{task_id}/execute
```

## 🏢 Subscription Tiers

### Free Tier
- 5 agents maximum
- 1,000 tasks per month
- Basic support
- Community access

### Basic Tier ($29/month)
- 25 agents maximum
- 10,000 tasks per month
- Email support
- Team collaboration (up to 5 users)

### Professional Tier ($99/month)
- 100 agents maximum
- 100,000 tasks per month
- Priority support
- Advanced analytics
- Team collaboration (up to 25 users)

### Enterprise Tier (Custom)
- Unlimited agents
- Unlimited tasks
- 24/7 support
- Custom integrations
- Unlimited users
- SLA guarantees

## 🛡️ Security Features

### Data Isolation
- **Tenant-Scoped Queries**: All data queries include tenant context
- **Row-Level Security**: Database-level tenant isolation
- **API Security**: All endpoints validate tenant access
- **Audit Logging**: Complete action tracking per tenant

### Authentication Security
- **JWT Tokens**: Secure stateless authentication
- **Refresh Tokens**: Automatic session renewal
- **Password Hashing**: Bcrypt with salt
- **Rate Limiting**: Protection against brute force attacks

### Authorization
- **Role-Based Access**: Granular permission control
- **Resource Ownership**: Users can only access their tenant's data
- **API Key Management**: Secure API access (future)

## 🧪 Testing Multi-Tenancy

### Create Test Organizations
```bash
# Create first organization
curl -X POST "http://localhost:8000/api/v1/tenants" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corp",
    "subdomain": "acme",
    "contact_email": "admin@acme.com",
    "contact_name": "John Doe",
    "subscription_tier": "professional"
  }'

# Create second organization  
curl -X POST "http://localhost:8000/api/v1/tenants" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Beta Ltd",
    "subdomain": "beta",
    "contact_email": "admin@beta.com",
    "contact_name": "Jane Smith",
    "subscription_tier": "basic"
  }'
```

### Register Users and Test Isolation
```bash
# Register admin for Acme Corp
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@acme.com",
    "password": "SecurePassword123",
    "full_name": "John Doe",
    "tenant_subdomain": "acme"
  }'

# Login and get token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@acme.com",
    "password": "SecurePassword123"
  }'

# Use token to create tenant-scoped agent
curl -X POST "http://localhost:8000/api/v1/agents" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "name": "Acme Agent",
    "description": "Agent for Acme Corp",
    "agent_type": "gpt-4"
  }'
```

## 🔧 Environment Configuration

### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://agent_user:agent_password@localhost:5432/agentcores_db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Security
SECRET_KEY=your-super-secret-jwt-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Environment
ENVIRONMENT=development

# Email (for invitations - future)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# AI API Keys
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

## 🚀 Deployment

### Production Deployment
```bash
# Production environment variables
export ENVIRONMENT=production
export DATABASE_URL=postgresql://user:pass@prod-db:5432/agentcores
export SECRET_KEY=production-secret-key

# Deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Run database migrations
docker-compose exec backend alembic upgrade head
```

### Kubernetes Deployment (Future)
- Helm charts for easy deployment
- Horizontal pod autoscaling
- Multi-region support
- Database clustering

## 🛠️ Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env

# Run migrations
alembic upgrade head

# Start with hot reload
uvicorn main:app --reload --port 8000
```

### Frontend Development  
```bash
cd frontend
npm install
npm start  # Starts on http://localhost:3000
```

### Database Management
```bash
# Create new migration
alembic revision --autogenerate -m "Add new feature"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 📈 Monitoring & Analytics

### Health Checks
- `GET /health` - Application health
- `GET /api/v1/tenants/health` - Tenant-specific health

### Metrics (Future)
- Per-tenant usage analytics
- Agent performance metrics
- Cost tracking per organization
- SLA monitoring

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/multi-tenant-feature`
3. Follow coding standards and add tests
4. Ensure tenant isolation in all new features
5. Submit pull request with detailed description

## � Documentation

- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Architecture Guide**: docs/ARCHITECTURE.md
- **Security Guide**: docs/SECURITY.md
- **Deployment Guide**: docs/DEPLOYMENT.md

## 🆘 Support

- **Issues**: GitHub Issues for bugs
- **Discussions**: GitHub Discussions for questions
- **Enterprise Support**: Contact for SLA and custom features

---

**Built for the Multi-Tenant AI Future** 🚀🏢