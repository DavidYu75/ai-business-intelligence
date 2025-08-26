# Development Setup Guide

This guide will help you set up the development environment for the Real-Time Business Intelligence Platform.

## Prerequisites

- **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18+** - [Download Node.js](https://nodejs.org/)
- **Docker & Docker Compose** - [Download Docker](https://www.docker.com/products/docker-desktop/)
- **Git** - [Download Git](https://git-scm.com/)

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd realtime-bi
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   pip install -r requirements/base.txt
   cp env.example .env
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Set up the frontend** (in a new terminal)
   ```bash
   cd frontend
   npm install
   cp env.example .env.local
   npm run dev
   ```

4. **Access the application**
   - Backend API: http://localhost:8000
   - Frontend: http://localhost:3000
   - API Documentation: http://localhost:8000/docs

## Backend Setup

### Using Virtual Environment (Recommended)

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   ```

3. **Activate virtual environment**
   ```bash
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements/base.txt
   ```

5. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

6. **Run the backend**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Using Poetry (Alternative)

1. **Install Poetry (if not installed)**
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Install dependencies**
   ```bash
   poetry install --no-root
   ```

3. **Run the backend**
   ```bash
   poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

4. **Run the frontend**
   ```bash
   npm run dev
   ```

## Database Setup

The application can use different databases for development and production.

### Development Database Options

#### Option 1: SQLite (Simplest)
Update your `.env` file:
```env
DATABASE_URL=sqlite:///./realtime_bi.db
```

#### Option 2: PostgreSQL (Recommended)
1. **Install PostgreSQL 15**
   ```bash
   # macOS (using Homebrew)
   brew install postgresql@15
   
   # Ubuntu/Debian
   sudo apt-get install postgresql-15
   ```

2. **Create database**
   ```sql
   CREATE DATABASE realtime_bi;
   CREATE USER realtime_bi_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE realtime_bi TO realtime_bi_user;
   ```

3. **Update your `.env` file**
   ```env
   DATABASE_URL=postgresql+asyncpg://realtime_bi_user:your_password@localhost:5432/realtime_bi
   ```

### Redis Setup (Optional for Development)

Redis is used for caching and session storage. For development, you can:

1. **Install Redis**
   ```bash
   # macOS (using Homebrew)
   brew install redis
   
   # Ubuntu/Debian
   sudo apt-get install redis-server
   ```

2. **Start Redis**
   ```bash
   redis-server
   ```

3. **Update your `.env` file**
   ```env
   REDIS_URL=redis://localhost:6379
   ```

## Development Tools

### Code Quality

The project includes several tools for maintaining code quality:

- **Black** - Python code formatting
- **isort** - Python import sorting
- **flake8** - Python linting
- **mypy** - Python type checking
- **ESLint** - JavaScript/TypeScript linting
- **Prettier** - Code formatting

### Running Quality Checks

**Backend:**
```bash
cd backend
poetry run black .
poetry run isort .
poetry run flake8 .
poetry run mypy .
```

**Frontend:**
```bash
cd frontend
npm run lint
npm run format:check
npm run type-check
```

### Testing

**Backend Tests:**
```bash
cd backend
poetry run pytest
poetry run pytest --cov=app --cov-report=html
```

**Frontend Tests:**
```bash
cd frontend
npm test
npm run test:coverage
npm run test:e2e
```

## Environment Variables

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql+asyncpg://realtime_bi_user:password@localhost:5432/realtime_bi
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=Real-Time BI Platform
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# ML/NLP Models
HUGGINGFACE_CACHE_DIR=./models
SPACY_MODEL=en_core_web_sm

# External APIs (optional)
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   - Check if ports 8000 or 3000 are already in use
   - Kill existing processes: `lsof -ti:8000 | xargs kill -9`
   - Or change ports in configuration

2. **Database connection issues**
   - Ensure PostgreSQL is running: `brew services start postgresql@15`
   - Check database credentials in .env file
   - Verify database exists and user has proper permissions

3. **Backend dependency issues**
   - Recreate virtual environment: `rm -rf venv && python3 -m venv venv`
   - Reinstall dependencies: `pip install -r requirements/base.txt`

4. **Frontend build issues**
   - Clear Next.js cache: `rm -rf .next`
   - Reinstall node modules: `rm -rf node_modules && npm install`

5. **Virtual environment issues**
   - Make sure virtual environment is activated: `source venv/bin/activate`
   - Check Python version: `python --version`
   - Recreate if needed: `rm -rf venv && python3 -m venv venv`

### Getting Help

- Check the [API Documentation](../api/)
- Review [Architecture Documentation](architecture.md)
- Open an issue on GitHub
- Contact the development team

## Next Steps

After setting up your development environment:

1. Read the [Architecture Documentation](architecture.md)
2. Review the [Contributing Guidelines](contributing.md)
3. Set up your IDE with recommended extensions
4. Run the test suite to ensure everything is working
5. Start with a simple feature or bug fix
