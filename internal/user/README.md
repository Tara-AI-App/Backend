# User Module

This module handles user authentication and management functionality.

## Features

- User registration
- User login with JWT authentication
- Password hashing using SHA-256
- User profile management
- Protected routes with JWT verification

## API Endpoints

### Authentication
- `POST /api/v1/users/register` - Register a new user
- `POST /api/v1/users/login` - Login user and get access token

### User Management
- `GET /api/v1/users/me` - Get current user information (requires authentication)
- `GET /api/v1/users/{user_id}` - Get user by ID

## Usage

### Register a new user
```bash
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepassword123",
    "country": "USA"
  }'
```

### Login user
```bash
curl -X POST "http://localhost:8000/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepassword123"
  }'
```

### Access protected route
```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Database Schema

The users table includes the following fields:
- `id` (UUID, Primary Key)
- `department_id` (UUID, Foreign Key)
- `position_id` (UUID, Foreign Key)
- `manager_id` (UUID, Foreign Key)
- `location_id` (UUID, Foreign Key)
- `name` (String, Required)
- `image` (String, Optional)
- `email` (String, Required, Unique)
- `password` (String, Required, Hashed)
- `country` (String, Optional)
- `created_at` (DateTime)

## Security

- Passwords are hashed using SHA-256
- JWT tokens are used for authentication
- Tokens expire after 1 hour
- All protected routes require valid JWT token in Authorization header