# AgentCores Multi-Tenant Deployment Guide

This guide covers deploying the multi-tenant version of AgentCores in various environments.

## Table of Contents

1. [Quick Start (Development)](#quick-start-development)
2. [Fresh Installation](#fresh-installation)
3. [Migration from Single-Tenant](#migration-from-single-tenant)
4. [Production Deployment](#production-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Security Considerations](#security-considerations)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)

## Quick Start (Development)

### Prerequisites
- Docker and Docker Compose
- Git

### Steps

```bash
# 1. Clone repository
git clone <repository-url>
cd AgentCores

# 2. Setup environment
cp backend/.env.example backend/.env

# 3. Start services
docker-compose up -d

# 4. Access application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### First-Time Setup

1. **Create Organization**: Visit http://localhost:3000/create-tenant
2. **Register Admin**: Create your organization admin account
3. **Login**: Access the dashboard
4. **Create Agents**: Start building your AI workflows

## Fresh Installation

### For New Deployments

If you're starting fresh with the multi-tenant version:

```bash
# 1. Start database
docker-compose up -d postgres redis

# 2. Run migrations
cd backend
python migrate_to_multitenant.py

# 3. Start all services
cd ..
docker-compose up -d
```

The system will create the multi-tenant database schema automatically.

## Migration from Single-Tenant

### Automated Migration

For existing single-tenant installations:

```bash
# 1. Backup existing data (recommended)
cd backend
python migrate_to_multitenant.py --backup

# 2. Run dry-run to see what will happen
python migrate_to_multitenant.py --dry-run

# 3. Perform migration
python migrate_to_multitenant.py
```

### Migration Process

The migration script will:

1. **Backup**: Create a database dump (if requested)
2. **Rename Tables**: Move existing tables to `*_old`
3. **Create Schema**: Set up new multi-tenant structure
4. **Migrate Data**: Move data to tenant-scoped tables
5. **Create Default**: Set up default organization and admin

### Post-Migration Setup

After migration, you'll have:

- **Default Organization**: "Default Organization" with subdomain "default"
- **Admin User**: `admin@agentcores.com` / `admin123`
- **Migrated Data**: All existing agents, tasks, and executions

**Important**: Change the default password immediately!

### Manual Migration Steps

If you prefer manual control:

```bash
# 1. Backup database
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Rename existing tables
psql $DATABASE_URL -c "ALTER TABLE agents RENAME TO agents_old;"
psql $DATABASE_URL -c "ALTER TABLE tasks RENAME TO tasks_old;"
psql $DATABASE_URL -c "ALTER TABLE task_executions RENAME TO task_executions_old;"

# 3. Run migrations
python -m alembic upgrade head

# 4. Verify migration
python -c "from app.database import engine; print('Migration successful!')"
```

## Production Deployment

### Environment Variables

Create a production `.env` file:

```bash
# Database
DATABASE_URL=postgresql://username:password@db-host:5432/agentcores_prod

# Redis
REDIS_URL=redis://redis-host:6379/0

# Security
SECRET_KEY=your-super-secret-production-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Environment
ENVIRONMENT=production

# CORS (if needed)
CORS_ORIGINS=["https://yourdomain.com"]

# Email (for invitations)
SMTP_HOST=smtp.yourmailserver.com
SMTP_PORT=587
SMTP_USERNAME=noreply@yourdomain.com
SMTP_PASSWORD=your-smtp-password

# AI Services
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

### Docker Production Deployment

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/agentcores
      - REDIS_URL=redis://redis:6379/0
      - ENVIRONMENT=production
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - postgres
      - redis
    ports:
      - "8000:8000"
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

  postgres:
    image: postgres:13
    environment:
      - POSTGRES_DB=agentcores
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

volumes:
  postgres_data:
```

Deploy:

```bash
# 1. Build and start
docker-compose -f docker-compose.prod.yml up -d

# 2. Run migrations
docker-compose -f docker-compose.prod.yml exec backend python migrate_to_multitenant.py

# 3. Create admin user (if needed)
docker-compose -f docker-compose.prod.yml exec backend python create_admin.py
```

### Kubernetes Deployment

Example Kubernetes manifests:

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: agentcores

---
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: agentcores-config
  namespace: agentcores
data:
  DATABASE_URL: "postgresql://user:pass@postgres:5432/agentcores"
  REDIS_URL: "redis://redis:6379/0"
  ENVIRONMENT: "production"

---
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: agentcores-secret
  namespace: agentcores
type: Opaque
stringData:
  SECRET_KEY: "your-secret-key-here"
  OPENAI_API_KEY: "your-openai-key"

---
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agentcores-backend
  namespace: agentcores
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agentcores-backend
  template:
    metadata:
      labels:
        app: agentcores-backend
    spec:
      containers:
      - name: backend
        image: agentcores/backend:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: agentcores-config
        - secretRef:
            name: agentcores-secret
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"

---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: agentcores-backend-service
  namespace: agentcores
spec:
  selector:
    app: agentcores-backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

Deploy to Kubernetes:

```bash
kubectl apply -f k8s/
kubectl -n agentcores exec deployment/agentcores-backend -- python migrate_to_multitenant.py
```

## Environment Configuration

### Required Environment Variables

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/db` | Yes |
| `SECRET_KEY` | JWT signing key (32+ chars) | `your-secret-key-here` | Yes |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` | Yes |
| `ENVIRONMENT` | Deployment environment | `production` | Yes |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiry | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiry | `7` |
| `CORS_ORIGINS` | Allowed CORS origins | `["*"]` |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |

### Database Configuration

For production, use managed PostgreSQL or configure PostgreSQL with:

```sql
-- Create database and user
CREATE DATABASE agentcores;
CREATE USER agentcores_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE agentcores TO agentcores_user;

-- Performance tuning
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET track_io_timing = on;
ALTER SYSTEM SET track_functions = 'all';
```

## Security Considerations

### Authentication Security

1. **Strong Secret Key**: Use a random 32+ character secret key
2. **Password Policy**: Enforce strong passwords
3. **Token Expiry**: Use short token expiry times
4. **HTTPS Only**: Always use HTTPS in production

### Database Security

1. **Connection Encryption**: Use SSL/TLS for database connections
2. **User Permissions**: Use dedicated database user with minimal permissions
3. **Network Isolation**: Restrict database access to application servers only

### Network Security

```yaml
# docker-compose.prod.yml security
services:
  backend:
    # ... other config
    networks:
      - app-network
    # Don't expose database ports publicly
  
  postgres:
    # Remove ports section for production
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
    internal: true  # Internal network only
```

### Environment Security

```bash
# Set proper file permissions
chmod 600 .env
chown root:root .env

# Use secrets management in production
export SECRET_KEY=$(cat /run/secrets/jwt_secret)
export DATABASE_PASSWORD=$(cat /run/secrets/db_password)
```

## Monitoring & Maintenance

### Health Checks

The application provides health check endpoints:

```bash
# Application health
curl http://localhost:8000/health

# Database health
curl http://localhost:8000/api/v1/health/db

# Detailed status
curl http://localhost:8000/api/v1/health/detailed
```

### Logging

Configure structured logging:

```python
# In production.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "module": "%(module)s"}'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/agentcores/app.log',
            'formatter': 'json',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file'],
    },
}
```

### Database Backups

Automated backup script:

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_URL="${DATABASE_URL}"

# Create backup
pg_dump "$DB_URL" | gzip > "$BACKUP_DIR/agentcores_backup_$DATE.sql.gz"

# Cleanup old backups (keep 30 days)
find "$BACKUP_DIR" -name "agentcores_backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: agentcores_backup_$DATE.sql.gz"
```

Schedule with cron:

```bash
# Daily backup at 2 AM
0 2 * * * /scripts/backup.sh
```

### Performance Monitoring

Use monitoring tools:

```yaml
# docker-compose.monitoring.yml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

## Troubleshooting

### Common Issues

#### Database Connection Errors

```bash
# Check database connection
docker-compose exec postgres psql -U user -d agentcores -c "SELECT 1;"

# Check database logs
docker-compose logs postgres
```

#### Migration Failures

```bash
# Check migration status
python -m alembic current

# Reset migrations (caution: data loss)
python -m alembic stamp head

# Manual migration
python -m alembic upgrade head --sql > migration.sql
psql $DATABASE_URL < migration.sql
```

#### Authentication Issues

```bash
# Verify JWT secret
python -c "from app.core.security import verify_token; print('JWT config OK')"

# Reset admin password
python scripts/reset_password.py admin@agentcores.com
```

#### Performance Issues

```bash
# Check database performance
docker-compose exec postgres psql -U user -d agentcores -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;"

# Check Redis status
docker-compose exec redis redis-cli info
```

### Logs and Debugging

```bash
# View application logs
docker-compose logs -f backend

# Enable debug logging
export LOG_LEVEL=DEBUG
docker-compose restart backend

# Database query logging
export SQLALCHEMY_LOG_LEVEL=INFO
```

### Recovery Procedures

#### From Backup

```bash
# Stop services
docker-compose down

# Restore database
psql $DATABASE_URL < backup_file.sql

# Restart services
docker-compose up -d

# Verify restoration
curl http://localhost:8000/health
```

#### Migration Rollback

```bash
# Note: Data migrations cannot be rolled back
# Restore from backup instead

# For schema-only rollbacks:
python -m alembic downgrade -1
```

### Getting Help

1. **Check Logs**: Always check application and database logs first
2. **Health Endpoints**: Use `/health` endpoints to verify system status
3. **Database Status**: Verify database connectivity and migrations
4. **Documentation**: Refer to API docs at `/docs` for endpoint details
5. **Community**: Check GitHub issues and discussions

---

## Quick Reference

### Common Commands

```bash
# Start development environment
docker-compose up -d

# Run migrations
python migrate_to_multitenant.py

# Create backup
pg_dump $DATABASE_URL > backup.sql

# View logs
docker-compose logs -f backend

# Reset database (development only)
docker-compose down -v && docker-compose up -d
```

### Important Files

- `backend/.env` - Environment configuration
- `backend/alembic/versions/` - Database migrations
- `docker-compose.yml` - Development setup
- `docker-compose.prod.yml` - Production setup

### Default Credentials

After migration or fresh install:
- **Email**: `admin@agentcores.com`
- **Password**: `admin123`
- **Organization**: `Default Organization`
- **Subdomain**: `default`

**⚠️ Change these immediately in production!**