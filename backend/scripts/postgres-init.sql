-- AgentCo-- Create user (if not exists) 
-- Note: Password is set via environment variable during container creation
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'agent_user') THEN
        -- User is created by container with POSTGRES_PASSWORD env var
        RAISE NOTICE 'User agent_user should be created by container initialization';
    ELSE
        RAISE NOTICE 'User agent_user already exists';
    END IF;
END
$$;ise Platform - PostgreSQL Multi-Database Initialization Script
-- Creates multi-database architecture for enterprise multi-tenancy
-- Each database serves a specific purpose:
-- - agentcores_db: Legacy/Demo database for compatibility
-- - agentcores_orgs: Organization database for multi-tenant organizations  
-- - agentcores_individuals: Individual users database for isolated accounts

-- Ensure we're connected to the correct database
\echo 'Initializing database: ' :DBNAME

-- Create user if not exists (for manual setup compatibility)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'agent_user') THEN
        CREATE USER agent_user WITH PASSWORD 'agent_password';
        RAISE NOTICE 'Created user: agent_user';
    ELSE
        RAISE NOTICE 'User agent_user already exists';
    END IF;
END
$$;

-- Grant privileges to agent_user
ALTER USER agent_user CREATEDB;
ALTER USER agent_user LOGIN;
GRANT ALL PRIVILEGES ON DATABASE agentcores_db TO agent_user;
GRANT ALL PRIVILEGES ON DATABASE agentcores_orgs TO agent_user;
GRANT ALL PRIVILEGES ON DATABASE agentcores_individuals TO agent_user;

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create enterprise schema
CREATE SCHEMA IF NOT EXISTS enterprise;

-- Set search path to include enterprise schema
ALTER DATABASE agentcores_db SET search_path TO public, enterprise;

-- Create tenants table for multi-tenancy
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    settings JSONB DEFAULT '{}',
    limits JSONB DEFAULT '{
        "max_agents": 10,
        "max_tasks_per_hour": 1000,
        "max_monthly_cost": 1000.0
    }',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) DEFAULT 'system'
);

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    UNIQUE(tenant_id, username),
    UNIQUE(tenant_id, email)
);

-- Create agents table
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    template_id VARCHAR(255) NOT NULL,
    provider VARCHAR(100) NOT NULL,
    model VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    config JSONB DEFAULT '{}',
    capabilities JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    UNIQUE(tenant_id, name)
);

-- Create tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    input_data JSONB DEFAULT '{}',
    output_data JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'pending',
    priority INTEGER DEFAULT 0,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    timeout_seconds INTEGER DEFAULT 300,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

-- Create events table for event sourcing
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    event_type VARCHAR(255) NOT NULL,
    entity_type VARCHAR(255) NOT NULL,
    entity_id UUID NOT NULL,
    event_data JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

-- Create cost_tracking table
CREATE TABLE IF NOT EXISTS cost_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    provider VARCHAR(100) NOT NULL,
    model VARCHAR(255) NOT NULL,
    operation_type VARCHAR(100) NOT NULL,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    cost_usd DECIMAL(10, 6) DEFAULT 0.0,
    currency VARCHAR(10) DEFAULT 'USD',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create analytics table
CREATE TABLE IF NOT EXISTS analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    metric_name VARCHAR(255) NOT NULL,
    metric_value DECIMAL(15, 6) NOT NULL,
    dimensions JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_tenants_name ON tenants(name);
CREATE INDEX IF NOT EXISTS idx_tenants_active ON tenants(is_active);

CREATE INDEX IF NOT EXISTS idx_users_tenant ON users(tenant_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(tenant_id, username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(tenant_id, email);

CREATE INDEX IF NOT EXISTS idx_agents_tenant ON agents(tenant_id);
CREATE INDEX IF NOT EXISTS idx_agents_name ON agents(tenant_id, name);
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);

CREATE INDEX IF NOT EXISTS idx_tasks_tenant ON tasks(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tasks_agent ON tasks(agent_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_created ON tasks(created_at);

CREATE INDEX IF NOT EXISTS idx_events_tenant ON events(tenant_id);
CREATE INDEX IF NOT EXISTS idx_events_entity ON events(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_created ON events(created_at);

CREATE INDEX IF NOT EXISTS idx_cost_tracking_tenant ON cost_tracking(tenant_id);
CREATE INDEX IF NOT EXISTS idx_cost_tracking_task ON cost_tracking(task_id);
CREATE INDEX IF NOT EXISTS idx_cost_tracking_created ON cost_tracking(created_at);

CREATE INDEX IF NOT EXISTS idx_analytics_tenant ON analytics(tenant_id);
CREATE INDEX IF NOT EXISTS idx_analytics_metric ON analytics(metric_name);
CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics(timestamp);

-- Create default tenant
INSERT INTO tenants (id, name, display_name, description, settings, limits)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'default',
    'Default Tenant',
    'Default tenant for AgentCores Enterprise Platform',
    '{"theme": "enterprise", "timezone": "UTC"}',
    '{
        "max_agents": 10,
        "max_tasks_per_hour": 1000,
        "max_monthly_cost": 1000.0
    }'
) ON CONFLICT (name) DO NOTHING;

-- Create default admin user (password: admin123 - hashed)
INSERT INTO users (id, tenant_id, username, email, hashed_password, full_name, is_superuser)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    'admin',
    'admin@agentcores.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewqLcw5YbLDqjJKW', -- admin123
    'Administrator',
    true
) ON CONFLICT (tenant_id, username) DO NOTHING;

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tenants_updated_at BEFORE UPDATE ON tenants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO agent_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO agent_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO agent_user;

-- Analytics and monitoring views
CREATE OR REPLACE VIEW tenant_stats AS
SELECT 
    t.id,
    t.name,
    t.display_name,
    COUNT(DISTINCT u.id) as user_count,
    COUNT(DISTINCT a.id) as agent_count,
    COUNT(DISTINCT tk.id) as task_count,
    COALESCE(SUM(ct.cost_usd), 0) as total_cost_usd,
    t.created_at
FROM tenants t
LEFT JOIN users u ON t.id = u.tenant_id AND u.is_active = true
LEFT JOIN agents a ON t.id = a.tenant_id AND a.status = 'active'
LEFT JOIN tasks tk ON t.id = tk.tenant_id
LEFT JOIN cost_tracking ct ON t.id = ct.tenant_id
WHERE t.is_active = true
GROUP BY t.id, t.name, t.display_name, t.created_at
ORDER BY t.created_at;

-- Performance monitoring view
CREATE OR REPLACE VIEW performance_metrics AS
SELECT 
    DATE_TRUNC('hour', created_at) as hour,
    tenant_id,
    COUNT(*) as task_count,
    AVG(EXTRACT(EPOCH FROM (completed_at - started_at))) as avg_duration_seconds,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_count,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_count
FROM tasks
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', created_at), tenant_id
ORDER BY hour DESC;

-- Cost analytics view
CREATE OR REPLACE VIEW cost_analytics AS
SELECT 
    DATE_TRUNC('day', created_at) as day,
    tenant_id,
    provider,
    model,
    SUM(cost_usd) as daily_cost_usd,
    SUM(total_tokens) as daily_tokens,
    COUNT(*) as operation_count
FROM cost_tracking
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', created_at), tenant_id, provider, model
ORDER BY day DESC;

-- Log successful initialization
INSERT INTO events (tenant_id, event_type, entity_type, entity_id, event_data, created_by)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'database.initialized',
    'system',
    '00000000-0000-0000-0000-000000000001',
    '{"message": "AgentCores Enterprise database initialized successfully", "version": "1.0.0"}',
    '00000000-0000-0000-0000-000000000001'
) ON CONFLICT DO NOTHING;