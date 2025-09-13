# User Domain

This directory contains the complete user domain following Clean Architecture principles.

## Structure

```
internal/user/
├── model/
│   ├── __init__.py
│   ├── user.py              # Domain entity (business logic)
│   └── user_dto.py          # Data Transfer Objects (DTOs)
├── repository/
│   ├── __init__.py
│   ├── user_repository.py   # Repository interface (abstraction)
│   └── user_repository_impl.py  # Repository implementation
├── service/
│   ├── __init__.py
│   └── user_use_cases.py    # Application use cases (orchestration)
├── handler/
│   ├── __init__.py
│   └── user_handler.py      # HTTP handlers (presentation layer)
└── README.md
```

## Components

### Model Layer
- **`user.py`**: Domain entity with business logic and validation
- **`user_dto.py`**: Request/Response DTOs for API communication

### Repository Layer
- **`user_repository.py`**: Abstract repository interface
- **`user_repository_impl.py`**: In-memory implementation

### Service Layer
- **`user_use_cases.py`**: Application use cases and orchestration

### Handler Layer
- **`user_handler.py`**: HTTP endpoints and request handling

## Usage

The user domain provides a complete CRUD API for managing users with:
- Create user
- Get user by ID
- Get all users
- Update user
- Delete user

All endpoints include proper error handling and validation.
