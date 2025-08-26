# Docker Development Environment Setup

This guide explains how to set up and run the Real-Time BI Platform using Docker.

## Prerequisites

- **Docker Desktop** installed and running
- **Docker Compose** (included with Docker Desktop)
- At least **4GB RAM** available for Docker
- **Git** for cloning the repository

## Quick Start

1. **Clone the repository** (if not already done)
   ```bash
   git clone <repository-url>
   cd realtime-bi
   ```

2. **Start the development environment**
   ```bash
   docker-compose up
   ```

3. **Access the services**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Database**: localhost:5432 (PostgreSQL)
   - **Cache**: localhost:6379 (Redis)

## Service Details

### PostgreSQL Database
- **Image**: postgres:15-alpine
- **Port**: 5432
- **Database**: realtime_bi
- **User**: realtime_bi_user
- **Password**: realtime_bi_password
- **Data Persistence**: `postgres_data` volume

### Redis Cache
- **Image**: redis:7-alpine
- **Port**: 6379
- **Data Persistence**: `redis_data` volume

### Backend API Server
- **Framework**: FastAPI (Python 3.11)
- **Port**: 8000
- **Hot Reload**: Enabled
- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs

### Frontend Development Server
- **Framework**: Next.js 14 (React 18)
- **Port**: 3000
- **Hot Reload**: Enabled
- **TypeScript**: Enabled
- **Tailwind CSS**: Configured

## Development Workflow

### Starting Services
```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Start specific service
docker-compose up backend
docker-compose up frontend
```

### Stopping Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: This will delete all data)
docker-compose down -v
```

### Viewing Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend

# Follow logs in real-time
docker-compose logs -f backend
```

### Rebuilding Services
```bash
# Rebuild all services
docker-compose build

# Rebuild specific service
docker-compose build backend
docker-compose build frontend

# Force rebuild (no cache)
docker-compose build --no-cache
```

### Accessing Containers
```bash
# Access backend container
docker-compose exec backend bash

# Access frontend container
docker-compose exec frontend sh

# Access database
docker-compose exec postgres psql -U realtime_bi_user -d realtime_bi
```

## Environment Variables

### Backend Environment
The backend uses these environment variables (configured in docker-compose.yml):
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: JWT secret key
- `BACKEND_CORS_ORIGINS`: Allowed CORS origins

### Frontend Environment
The frontend uses these environment variables:
- `NEXT_PUBLIC_API_URL`: Backend API URL
- `NEXT_PUBLIC_WS_URL`: WebSocket URL

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using the port
   lsof -i :8000
   lsof -i :3000
   
   # Kill the process or change ports in docker-compose.yml
   ```

2. **Container won't start**
   ```bash
   # Check logs
   docker-compose logs <service-name>
   
   # Rebuild container
   docker-compose build --no-cache <service-name>
   ```

3. **Database connection issues**
   ```bash
   # Check if database is running
   docker-compose ps postgres
   
   # Check database logs
   docker-compose logs postgres
   ```

4. **Permission issues**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   ```

### Performance Issues

1. **Increase Docker resources**
   - Open Docker Desktop
   - Go to Settings > Resources
   - Increase Memory to at least 4GB
   - Increase CPU to at least 2 cores

2. **Clean up Docker**
   ```bash
   # Remove unused containers, networks, images
   docker system prune
   
   # Remove all unused volumes (WARNING: This will delete all data)
   docker volume prune
   ```

## Development Tips

### Hot Reload
Both frontend and backend support hot reload:
- Backend: Code changes automatically restart the server
- Frontend: Code changes automatically refresh the browser

### Database Migrations
When you add database models later, you'll run migrations inside the backend container:
```bash
docker-compose exec backend alembic upgrade head
```

### Installing New Dependencies

**Backend (Python)**:
```bash
# Add to requirements/base.txt, then rebuild
docker-compose build backend
```

**Frontend (Node.js)**:
```bash
# Add to package.json, then rebuild
docker-compose build frontend
```

### Debugging
- Backend logs are available via `docker-compose logs backend`
- Frontend logs are available via `docker-compose logs frontend`
- Use browser dev tools for frontend debugging
- API requests can be tested via http://localhost:8000/docs

## Next Steps

After the development environment is running:

1. **Verify all services are healthy**
   - Check http://localhost:8000/health
   - Check http://localhost:3000

2. **Explore the API documentation**
   - Visit http://localhost:8000/docs

3. **Start development**
   - Begin implementing features following the Day 1-35 plan
   - Use the hot reload for rapid development

4. **Set up your IDE**
   - Configure your IDE to work with the Docker containers
   - Set up debugging if needed
