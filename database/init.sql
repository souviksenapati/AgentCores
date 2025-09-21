-- Create database if it doesn't exist
CREATE DATABASE agentcores_db;

-- Create user if it doesn't exist
CREATE USER agent_user WITH PASSWORD 'agent_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE agentcores_db TO agent_user;

-- Connect to the database
\c agentcores_db;

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO agent_user;