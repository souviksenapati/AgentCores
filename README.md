# AgentCores - Phase 1 MVP

🚀 **AI Agent Management Platform** - Built with Python/FastAPI backend and React frontend

## 🏗️ Architecture Overview

AgentCores is a next-generation AI agent management platform designed for enterprise-scale deployment. This Phase 1 MVP provides core agent lifecycle management with the foundation for scaling to 10,000+ concurrent agents.

### Core Components:
- **Backend API**: FastAPI with PostgreSQL
- **Frontend Dashboard**: React with Material-UI
- **Database**: PostgreSQL with Redis caching
- **Containerization**: Docker Compose for easy deployment

## 🚀 Quick Start

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

**🔥 Hot Reload Enabled**: Code changes automatically refresh without rebuilds!
- **Frontend**: Browser auto-refreshes on save
- **Backend**: Server auto-restarts on save
- **Fast Builds**: Dependencies cached, only code changes rebuild

### 3. Access the Application
- **Frontend Dashboard**: http://localhost:3000 (with hot reload)
- **Backend API**: http://localhost:8000 (with hot reload)
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 4. Development Experience
**⚡ Optimized for Speed:**
- First build: 5-8 minutes
- Code changes: 30 seconds (95% faster!)
- Dependencies cached automatically
- No rebuild needed for code changes

### 4. Create Your First Agent
1. Open http://localhost:3000
2. Navigate to "Agents" tab
3. Click "Create Agent"
4. Fill in agent details:
   - Name: "My First Agent"
   - Type: "gpt-4"
   - Description: "Test agent for text processing"

## 🛠️ Local Development

### Backend Development
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env

# Start PostgreSQL (via Docker)
docker run -d --name postgres \
  -e POSTGRES_DB=agentcores_db \
  -e POSTGRES_USER=agent_user \
  -e POSTGRES_PASSWORD=agent_password \
  -p 5432:5432 postgres:13

# Run migrations
alembic upgrade head

# Start development server
uvicorn main:app --reload --port 8000
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## 📊 Features

### ✅ Implemented (Phase 1)

#### Agent Management
- ✅ Create, read, update, delete agents
- ✅ Start/stop agent operations
- ✅ Agent status tracking (idle, running, paused, error)
- ✅ Multiple agent types (GPT-4, Claude, Custom)
- ✅ Agent configuration and capabilities

#### Task Management
- ✅ Create and execute tasks
- ✅ Multiple task types:
  - **Text Processing**: uppercase, lowercase, word count
  - **API Calls**: HTTP requests with response handling
  - **Workflows**: Multi-step task execution
- ✅ Task priority levels (1-5)
- ✅ Task execution tracking and results

#### Web Dashboard
- ✅ Responsive Material-UI interface
- ✅ Real-time agent and task statistics
- ✅ Agent management interface
- ✅ Task creation and execution
- ✅ Status monitoring and analytics

#### Infrastructure
- ✅ FastAPI with automatic OpenAPI documentation
- ✅ PostgreSQL with SQLAlchemy ORM
- ✅ Redis for caching and session management
- ✅ Docker containerization
- ✅ Alembic database migrations

### 🔄 Task Types Explained

#### Text Processing
Process text with various operations:
```json
{
  "name": "Process User Input",
  "task_type": "text_processing",
  "input_data": {
    "text": "Hello World",
    "operation": "uppercase"  // options: uppercase, lowercase, word_count, echo
  }
}
```

#### API Calls
Make HTTP requests to external services:
```json
{
  "name": "Fetch Weather Data",
  "task_type": "api_call",
  "input_data": {
    "url": "https://api.openweathermap.org/data/2.5/weather",
    "method": "GET",
    "headers": {"Authorization": "Bearer token"},
    "data": {"q": "London"}
  }
}
```

#### Workflows
Execute multi-step processes:
```json
{
  "name": "Data Processing Workflow",
  "task_type": "workflow",
  "input_data": {
    "steps": [
      {"type": "delay", "seconds": 2},
      {"type": "log", "message": "Processing started"}
    ]
  }
}
```

## 🗄️ Database Schema

### Agents Table
```sql
- id (UUID, Primary Key)
- name (String, Required)
- description (Text)
- agent_type (String: gpt-4, claude, custom)
- version (String, Default: "1.0.0")
- status (Enum: idle, running, paused, error, terminated)
- configuration (JSON)
- capabilities (JSON Array)
- resources (JSON)
- created_at, updated_at, last_active (Timestamps)
```

### Tasks Table
```sql
- id (UUID, Primary Key)
- name (String, Required)
- description (Text)
- task_type (String: text_processing, api_call, workflow)
- input_data (JSON)
- output_schema (JSON)
- priority (Integer 1-5)
- timeout_seconds (Integer, Default: 300)
- retry_count (Integer, Default: 3)
- agent_id (Foreign Key)
- created_at, updated_at (Timestamps)
```

### Task Executions Table
```sql
- id (UUID, Primary Key)
- status (Enum: pending, running, completed, failed, cancelled)
- result (JSON)
- error_message (Text)
- execution_time_ms (Integer)
- started_at, completed_at, created_at (Timestamps)
- agent_id, task_id (Foreign Keys)
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Database
DATABASE_URL=postgresql://agent_user:agent_password@localhost:5432/agentcores_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development

# AI API Keys (for future use)
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

## 📈 Monitoring and Health Checks

### Health Endpoints
- `GET /` - Basic health check
- `GET /api/v1/health` - API health check

### Metrics (Future Enhancement)
- Agent performance metrics
- Task execution statistics
- Resource utilization tracking
- Cost analysis per agent

## 🧪 Testing

### API Testing with curl
```bash
# Create an agent
curl -X POST "http://localhost:8000/api/v1/agents" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Agent",
    "description": "A test agent",
    "agent_type": "gpt-4",
    "capabilities": ["text_processing"]
  }'

# Start the agent
curl -X POST "http://localhost:8000/api/v1/agents/{agent_id}/start"

# Create a task
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Task",
    "task_type": "text_processing",
    "agent_id": "{agent_id}",
    "input_data": {
      "text": "Hello World",
      "operation": "uppercase"
    }
  }'

# Execute the task
curl -X POST "http://localhost:8000/api/v1/tasks/{task_id}/execute"
```

## 🚧 Roadmap - Next Phases

### Phase 2: Multi-Agent Coordination (Planned)
- [ ] Agent-to-agent communication
- [ ] Task delegation and coordination
- [ ] Message queues with Celery
- [ ] Real-time WebSocket updates

### Phase 3: Enterprise Features (Planned)
- [ ] User authentication and authorization
- [ ] Role-based access control
- [ ] Advanced monitoring and analytics
- [ ] Integration with external AI services
- [ ] Kubernetes deployment

### Phase 4: Advanced Intelligence (Planned)
- [ ] Machine learning for task optimization
- [ ] Predictive scaling
- [ ] Behavioral analytics
- [ ] Cost optimization algorithms

## 🛠️ Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

#### Port Conflicts
```bash
# Check what's using port 8000
netstat -tulpn | grep :8000

# Use different ports in docker-compose.yml
ports:
  - "8001:8000"  # Change external port
```

#### Frontend Build Issues
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check this README and API docs at `/docs`
- **Issues**: Create GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions

---

**Built with ❤️ for the AI Agent Revolution** 🚀