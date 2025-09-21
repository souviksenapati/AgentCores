# AgentCores Multi-Tenant Setup

## Quick Start

AgentCores is now a full multi-tenant SaaS application with tenant isolation, authentication, and role-based access control.

### 🚀 Setup Instructions

1. **Start the services**:
   ```bash
   docker-compose up -d
   ```
   
   This will:
   - Start PostgreSQL database
   - Initialize multi-tenant database with default data
   - Start Redis cache
   - Start the FastAPI backend on port 8000
   - Start the React frontend on port 3000

2. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

3. **Default Login Credentials**:
   - Organization: `AgentCores Demo`
   - Email: `admin@demo.agentcores.com`
   - Password: `admin123`
   - ⚠️ **Change password after first login!**

### 🏢 Multi-Tenant Features

- **Tenant Isolation**: Complete data separation between organizations
- **User Management**: Invite users, manage roles (owner, admin, member)
- **Authentication**: JWT-based auth with organization context
- **Role-Based Access**: Different permissions for different roles
- **Audit Logging**: Track all user actions for compliance
- **Single Domain**: All organizations use the same domain (agentcores.com/app)

### 🔧 Development Setup

If you want to run without Docker:

1. **Start PostgreSQL**:
   ```bash
   docker run -d --name postgres -p 5432:5432 -e POSTGRES_DB=agentcores_db -e POSTGRES_USER=agent_user -e POSTGRES_PASSWORD=agent_password postgres:13
   ```

2. **Setup Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   python setup_database.py
   uvicorn main:app --reload
   ```

3. **Setup Frontend**:
   ```bash
   cd frontend
   npm install
   npm start
   ```

### 📊 Database Schema

The multi-tenant database includes:

- **Tenants**: Organizations with their own data space
- **Users**: Multi-role users (owner, admin, member) per tenant
- **Agents**: AI agents isolated by tenant
- **Tasks**: Task management with tenant context
- **Audit Logs**: Compliance tracking
- **Invitations**: User invitation system

### 🔒 Security Features

- JWT authentication with tenant context
- Password hashing with bcrypt
- API route protection
- Tenant data isolation
- Role-based access control
- CORS protection

### 🧪 Testing

Run the test suite:
```bash
cd backend
pytest tests/
```

### 📝 Environment Variables

Key environment variables (in docker-compose.yml):

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT signing key (change in production!)
- `ENVIRONMENT`: development/production
- `REACT_APP_API_URL`: Frontend API endpoint

### 🛠️ Troubleshooting

**Database Issues**:
```bash
# Reset database
docker-compose down -v
docker-compose up -d
```

**Backend Issues**:
```bash
# Check logs
docker-compose logs backend

# Restart backend only
docker-compose restart backend
```

**Frontend Issues**:
```bash
# Check logs
docker-compose logs frontend

# Clear React cache
docker-compose exec frontend npm start
```

### 🎯 Next Steps

1. Change default password
2. Create your organization 
3. Invite team members
4. Start creating AI agents
5. Set up production environment with proper SECRET_KEY

### 🔄 Migration from Single-Tenant

If you have existing AgentCores data, the system will detect existing tables and preserve data while adding multi-tenant capabilities.

---

**AgentCores Multi-Tenant** - AI Agent Management Platform