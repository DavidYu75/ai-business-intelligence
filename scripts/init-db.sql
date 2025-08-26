-- Initialize Real-Time BI Platform Database
-- This script runs when the PostgreSQL container starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Set timezone
SET timezone = 'UTC';

-- Create additional schemas if needed
CREATE SCHEMA IF NOT EXISTS analytics;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA public TO realtime_bi_user;
GRANT ALL PRIVILEGES ON SCHEMA analytics TO realtime_bi_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO realtime_bi_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA analytics TO realtime_bi_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO realtime_bi_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA analytics TO realtime_bi_user;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO realtime_bi_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO realtime_bi_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA analytics GRANT ALL ON TABLES TO realtime_bi_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA analytics GRANT ALL ON SEQUENCES TO realtime_bi_user;
