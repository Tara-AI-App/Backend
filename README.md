# Tara Backend API

A modern FastAPI application with Domain Driven Design, AI-powered learning management, OAuth integration, and comprehensive HR management features.

## 🎯 Features

- **AI-Powered Learning**: Generate courses and guides using AI
- **Authentication & Authorization**: JWT-based auth with OAuth support (GitHub, Google)
- **Learning Management System**: Courses, lessons, quizzes, and learning paths
- **HR Management**: Employee, company, and department management
- **Chat System**: Interactive chat with AI-powered assistance
- **Database Migrations**: Automated schema management with Alembic
- **RESTful API**: Clean, well-documented API endpoints

## 🏗️ Project Structure

```
tara-be/
├── app/                          # FastAPI application core
│   ├── main.py                   # FastAPI app creation & routing
│   ├── config.py                 # Application settings & env vars
│   └── database/                 # Database configuration
│       ├── connection.py         # SQLAlchemy connection
│       └── models.py             # SQLAlchemy models
│
├── internal/                     # Business logic layer
│   ├── ai/                       # AI-powered features
│   │   ├── chat/                 # AI chat system
│   │   ├── course/               # AI course generation
│   │   └── guide/               # AI guide generation
│   ├── auth/                     # Authentication middleware
│   ├── course/                   # Course management
│   ├── guide/                    # Guide management
│   ├── hr/                       # HR management
│   │   ├── company/             # Company management
│   │   ├── department/          # Department management
│   │   └── employee/           # Employee management
│   ├── oauth/                    # OAuth integration
│   └── user/                    # User management
│
├── alembic/                     # Database migrations
│   ├── versions/                # Migration files
│   └── env.py                   # Alembic environment config
│
├── scripts/                     # Utility scripts
│   ├── db_manager.py            # Database management
│   ├── init_db.py               # Database initialization
│   └── migrate.py               # Migration helpers
│
├── tests/                       # Test files
│   ├── conftest.py              # Test configuration
│   └── test_items.py          # Test examples
│
├── requirements.txt             # Python dependencies
├── alembic.ini                  # Alembic configuration
├── Dockerfile                   # Docker container config
├── run.py                       # Development entry point
└── main.py                      # Legacy entry point
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 12+ (or compatible database)
- pip

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Run database migrations
alembic upgrade head

# Or initialize database manually
python scripts/init_db.py
```

### 3. Run the Application

```bash
# Development mode with auto-reload
python run.py

# Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 9000

# Production mode
python main.py
```

### 4. Docker Deployment

```bash
# Build the Docker image
docker build -t tara-backend .

# Run the container
docker run -p 9000:9000 --env-file .env tara-backend
```

## 🗄️ Database Migrations

### Create a New Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Create empty migration
alembic revision -m "Description of changes"
```

### Apply Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade <revision_id>

# Rollback to previous migration
alembic downgrade -1

# Rollback to specific migration
alembic downgrade <revision_id>
```

### Check Migration Status

```bash
# Show current revision
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic show head
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov=internal
```

For detailed API documentation, visit `/docs` when the application is running.

## 🏛️ Architecture

This project follows a **Clean Architecture** approach with **Domain Driven Design** principles:

### Core Principles

- **Separation of Concerns**: Clear boundaries between layers
- **Dependency Inversion**: High-level modules don't depend on low-level modules
- **Single Responsibility**: Each module has one clear purpose
- **Repository Pattern**: Abstraction of data access logic
- **Service Layer**: Encapsulates business logic

### Architecture Layers

```
┌─────────────────────────────────────────┐
│         API Layer (Handlers)            │  ← HTTP endpoints, request/response
├─────────────────────────────────────────┤
│         Business Logic (Services)       │  ← Core business rules
├─────────────────────────────────────────┤
│         Data Access (Repositories)      │  ← Database operations
├─────────────────────────────────────────┤
│         Database Models (SQLAlchemy)    │  ← ORM models
└─────────────────────────────────────────┘
```

### Layer Responsibilities

1. **Handler Layer** (`internal/*/handler/`)
   - HTTP request/response handling
   - Input validation
   - Authentication & authorization
   - Route definitions

2. **Service Layer** (`internal/*/service/`)
   - Business logic orchestration
   - Transaction management
   - Cross-cutting concerns
   - Domain operations

3. **Repository Layer** (`internal/*/repository/`)
   - Data persistence
   - Query construction
   - Database abstraction
   - CRUD operations

4. **Model Layer** (`internal/*/model/`)
   - Data Transfer Objects (DTOs)
   - Domain entities
   - Validation schemas
   - Request/response models

5. **Database Layer** (`app/database/`)
   - SQLAlchemy ORM models
   - Database configuration
   - Connection management
   - Migration scripts (Alembic)

### Features Integration

- **JWT Authentication**: Token-based auth with middleware
- **OAuth Integration**: GitHub and Google OAuth flows
- **AI Integration**: External AI API for course/guide generation
- **CORS**: Configured for frontend communication
- **Database Migrations**: Alembic for schema management

## 🛠️ Development

### Running in Development Mode

```bash
# Start with hot-reload
python run.py

# Or with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 9000
```

### Database Development

```bash
# Create new migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Apply all pending migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Show current database revision
alembic current

# Show migration history
alembic history
```

### Adding New Features

1. **Create Database Models**: Add SQLAlchemy models in `app/database/models.py`
2. **Generate Migration**: Run `alembic revision --autogenerate -m "Description"`
3. **Create DTOs**: Add request/response models in `internal/{domain}/model/`
4. **Implement Repository**: Add data access logic in `internal/{domain}/repository/`
5. **Implement Service**: Add business logic in `internal/{domain}/service/`
6. **Create Handlers**: Add API endpoints in `internal/{domain}/handler/`
7. **Register Routes**: Import and include router in `app/main.py`
8. **Add Tests**: Create tests in `tests/` directory

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov=internal --cov-report=html

# Run specific test file
pytest tests/test_items.py

# Run with verbose output
pytest -v
```

### Code Quality

Recommended tools (not included in requirements.txt):

```bash
# Format code with black
pip install black
black .

# Sort imports with isort
pip install isort
isort .

# Lint with flake8
pip install flake8
flake8 .

# Type checking with mypy
pip install mypy
mypy .
```

### Docker Development

```bash
# Build image
docker build -t tara-backend .

# Run container
docker run -p 9000:9000 \
  --env-file .env \
  -v $(pwd):/app \
  tara-backend

# Run with database mounted
docker run -p 9000:9000 \
  --env-file .env \
  --link postgres:db \
  tara-backend
```

### Hot Reload in Docker

For development with hot reload in Docker, modify `run.py` to use uvicorn's reload feature and mount your code as a volume.

## 📚 Tech Stack

- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL with SQLAlchemy
- **Migrations**: Alembic
- **Authentication**: JWT with OAuth (GitHub, Google)
- **HTTP Client**: httpx
- **Validation**: Pydantic
- **Testing**: pytest
- **Container**: Docker

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Check if database is running
psql -U postgres -c "SELECT 1"

# Test connection from Python
python -c "from app.database.connection import engine; engine.connect()"
```

### Migration Issues

```bash
# If migrations fail, check current state
alembic current

# View migration history
alembic history

# Create backup before migration
pg_dump -U postgres tara > backup.sql

# Fix migration conflicts
# Edit the conflicting migration file in alembic/versions/
```

### Port Already in Use

```bash
# Find process using port 9000
lsof -i :9000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn app.main:app --port 9001
```

### Environment Variables Not Loading

```bash
# Verify .env file exists
ls -la .env

# Check if variables are loaded
python -c "from app.config import settings; print(settings.DATABASE_URL)"
```

### Import Errors

```bash
# Make sure you're in the correct directory
cd tara-be

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python path
python -c "import sys; print(sys.path)"
```

## 🚀 Deployment

### Production Deployment

1. **Set Environment Variables**: Configure all required environment variables
2. **Run Migrations**: `alembic upgrade head`
3. **Start Application**: `uvicorn app.main:app --host 0.0.0.0 --port 9000`

### Docker Production

```bash
# Build optimized image
docker build -t tara-backend:latest .

# Run with production settings
docker run -d \
  --name tara-backend \
  -p 9000:9000 \
  --env-file .env.production \
  --restart unless-stopped \
  tara-backend:latest
```

### Cloud Deployment (Google Cloud Run)

The project is configured for Google Cloud Run deployment. See `.github/workflows/` for CI/CD configuration.

```bash
# Deploy to Cloud Run
gcloud run deploy tara-backend \
  --source . \
  --region us-central1 \
  --port 9000 \
  --env-vars-file env_vars.yaml
```

## 📝 License

This project is proprietary software. All rights reserved.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Contact

For questions or support, please contact the development team.