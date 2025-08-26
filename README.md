# Real-Time Business Intelligence Platform

A comprehensive BI platform that allows non-technical users to query business data using natural language, with real-time collaborative dashboards and sub-second response times.

## Features

- Natural language to SQL conversion with 95% accuracy
- Sub-3-second query response times
- Support for 1000+ concurrent users
- Multi-database connectivity (PostgreSQL, MySQL, SQLite)
- Real-time collaborative dashboards
- Enterprise-grade security and authentication

## Technology Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy, asyncpg
- **Frontend**: React 18, TypeScript, Next.js, Tailwind CSS
- **Database**: PostgreSQL 15 (primary), Redis 7 (cache)
- **ML/NLP**: Hugging Face Transformers, spaCy, PyTorch
- **Infrastructure**: Docker, Kubernetes, WebSocket

## Quick Start

### Backend Setup

```bash
# Clone the repository
git clone <repository-url>
cd realtime-bi

# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements/base.txt

# Set up environment variables
cp env.example .env

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp env.example .env.local

# Start the development server
npm run dev
```

### Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Project Structure

```
realtime-bi/
├── backend/                 # Python FastAPI backend
│   ├── app/                # Main application code
│   ├── tests/              # Backend tests
│   ├── alembic/            # Database migrations
│   ├── requirements/       # Python dependencies
│   └── venv/               # Virtual environment (created locally)
├── frontend/               # React Next.js frontend
│   ├── src/                # Source code
│   ├── public/             # Static assets
│   └── tests/              # Frontend tests
├── infrastructure/         # Infrastructure and deployment
│   ├── k8s/                # Kubernetes manifests
│   └── terraform/          # Infrastructure as Code
├── docs/                   # Documentation
└── scripts/                # Utility scripts
```

## Development

### Prerequisites

- **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18+** - [Download Node.js](https://nodejs.org/)
- **PostgreSQL 15** (optional, can use SQLite for development)
- **Redis** (optional for development)

### Backend Development

The backend uses:
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **Poetry/Virtual Environment** - Dependency management
- **Uvicorn** - ASGI server with hot reload

### Frontend Development

The frontend uses:
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first styling
- **React Query** - Server state management

### Database Options

For development, you can use:
- **SQLite** (simplest) - Update `DATABASE_URL` in `.env` to `sqlite:///./realtime_bi.db`
- **PostgreSQL** (recommended) - Install PostgreSQL 15 and create a database
- **Docker PostgreSQL** - Run PostgreSQL in Docker if you prefer

See [Development Setup Guide](docs/developer/setup.md) for detailed instructions.
