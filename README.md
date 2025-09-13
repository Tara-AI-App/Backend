# Tara API

A FastAPI application with Domain Driven Design, AI integration, and database migrations.

## 🏗️ Project Structure

```
tara/
├── app/                          # FastAPI application
│   ├── main.py                   # FastAPI app creation
│   ├── config.py                 # Application settings
│   └── database/                 # Database configuration
│       ├── connection.py         # Database connection
│       └── models.py             # SQLAlchemy models
├── internal/                     # Internal business logic
│   ├── domain/                   # Business domains
│   │   └── item/                 # Item domain
│   │       ├── handler/          # API endpoints
│   │       ├── service/          # Business logic
│   │       ├── repository/       # Data access
│   │       └── model/            # Domain models
│   └── ai/                       # AI module
│       ├── handler/              # AI API endpoints
│       ├── service/              # AI business logic
│       ├── repository/           # AI data access
│       └── model/                # AI models & DTOs
├── alembic/                      # Database migrations
├── scripts/                      # Utility scripts
├── tests/                        # Test files
├── requirements/                 # Dependencies
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── run.py                        # Entry point
└── main.py                       # Legacy entry point
```

## 🚀 Quick Start

### 1. Environment Setup

Copy the environment template and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` with your actual credentials:

```bash
# Database Configuration (REQUIRED)
DATABASE_URL=postgresql://your_username:your_password@localhost:5432/your_database
```

### 2. Install Dependencies

```bash
# For development
pip install -r requirements/dev.txt

# For production
pip install -r requirements/prod.txt
```

### 3. Database Setup

```bash
# Run migrations
alembic upgrade head

# Or initialize database manually
python scripts/init_db.py
```

### 3. Run the Application

```bash
# Using run.py
python run.py

# Using uvicorn directly
uvicorn app.main:app --reload

# Using legacy main.py
python main.py
```

### 4. Access the API

- **API**: `http://localhost:8000`
- **Interactive Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`

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

## 📋 API Endpoints

### Items
- `GET /api/v1/items/` - Get all items with statistics
- `GET /api/v1/items/{item_id}` - Get item by ID
- `POST /api/v1/items/` - Create new item
- `PUT /api/v1/items/{item_id}` - Update item
- `DELETE /api/v1/items/{item_id}` - Delete item
- `GET /api/v1/items/expensive/?threshold=100.00` - Get expensive items

### AI
- `POST /api/v1/ai/chat` - Chat with AI assistant
- `POST /api/v1/ai/analyze` - Analyze items with AI
- `POST /api/v1/ai/recommendations` - Get AI recommendations
- `POST /api/v1/ai/enhance-description/{item_id}` - Enhance descriptions
- `POST /api/v1/ai/analyze-pricing/{item_id}` - Analyze pricing
- `GET /api/v1/ai/conversations/{user_id}` - Get conversation history
- `GET /api/v1/ai/analyses/{item_id}` - Get item analyses
- `GET /api/v1/ai/recommendations/{user_id}` - Get recommendation history

### System
- `GET /` - Welcome message
- `GET /health` - Health check

## 🔧 Configuration

Copy `.env.example` to `.env` and modify settings:

```bash
cp .env.example .env
```

### Database Configuration

```env
# PostgreSQL (recommended)
DATABASE_URL=postgresql://user:password@localhost:5432/tara

# SQLite (for development)
DATABASE_URL=sqlite:///./tara.db

# MySQL
DATABASE_URL=mysql://user:password@localhost:3306/tara
```

## 🏛️ Architecture

This project follows a **hybrid approach** combining:

- **Domain Driven Design** principles
- **FastAPI best practices**
- **Clean Architecture** patterns
- **Database migrations** with Alembic
- **AI integration** with multiple providers

### Layers:
1. **Handler Layer** - API endpoints and HTTP handling
2. **Service Layer** - Business logic and use cases
3. **Repository Layer** - Data access and persistence
4. **Model Layer** - Domain entities and DTOs
5. **Database Layer** - SQLAlchemy models and migrations

## 🛠️ Development

### Code Quality
```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8 .

# Type checking
mypy .
```

### Database Development
```bash
# Create new migration
alembic revision --autogenerate -m "Add new feature"

# Apply migrations
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### Adding New Features
1. Add domain models in `internal/domain/model/` or `internal/ai/model/`
2. Add database models in `app/database/models.py`
3. Create migration: `alembic revision --autogenerate -m "Description"`
4. Add business logic in `internal/*/service/`
5. Add data access in `internal/*/repository/`
6. Add API endpoints in `internal/*/handler/`
7. Add tests in `tests/`