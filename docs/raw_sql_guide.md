# Raw SQL Queries Guide

This guide explains how to use raw SQL queries in the UserRepository implementations.

## Overview

Raw SQL queries provide several advantages over ORM-based approaches:
- **Performance**: Direct SQL execution is often faster than ORM mapping
- **Complex Queries**: Easier to write complex JOINs, aggregations, and subqueries
- **Database-Specific Features**: Access to database-specific functions and optimizations
- **Fine-Grained Control**: Precise control over query execution and optimization

## Available Implementations

### 1. UserRepositoryDB
Basic raw SQL implementation with standard CRUD operations.

**Features:**
- Standard CRUD operations (Create, Read, Update, Delete)
- Custom query methods (age range, name pattern search)
- Pagination support
- User count queries

### 2. UserRepositoryAdvanced
Advanced raw SQL implementation with complex queries and analytics.

**Features:**
- All basic CRUD operations
- Complex JOIN queries with statistics
- Advanced search with multiple filters
- User activity summaries
- Department-based queries
- Performance optimizations

## Usage Examples

### Basic Operations

```python
from internal.user.repository.user_repository_db import UserRepositoryDB
from internal.user.model.user import User

# Initialize repository
repo = UserRepositoryDB()

# Create a user
user = User(id=None, name="John Doe", email="john@example.com", age=30)
saved_user = await repo.save(user)

# Find user by ID
found_user = await repo.find_by_id(saved_user.id)

# Find all users
all_users = await repo.find_all()

# Search by name pattern
search_results = repo.find_users_by_name_pattern("John")

# Get user count
count = repo.get_user_count()
```

### Advanced Operations

```python
from internal.user.repository.user_repository_advanced import UserRepositoryAdvanced

# Initialize advanced repository
repo = UserRepositoryAdvanced()

# Advanced search with filters
filters = {
    'min_age': 25,
    'max_age': 40,
    'department': 'Engineering'
}
results = repo.search_users_advanced("", filters)

# Get users with course statistics
users_with_stats = repo.find_users_with_statistics()

# Get detailed user activity
activity = repo.get_user_activity_summary(user_id)
```

## Raw SQL Query Examples

### Simple SELECT Query
```sql
SELECT id, name, email, age, created_at
FROM users
ORDER BY created_at DESC
```

### Complex JOIN with Statistics
```sql
SELECT 
    u.id, u.name, u.email, u.age, u.created_at,
    COUNT(c.id) as course_count,
    AVG(c.progress) as avg_progress,
    MAX(c.created_at) as last_course_date
FROM users u
LEFT JOIN courses c ON u.id = c.user_id
GROUP BY u.id, u.name, u.email, u.age, u.created_at
ORDER BY u.created_at DESC
```

### Advanced Search with Multiple Filters
```sql
SELECT DISTINCT u.id, u.name, u.email, u.age, u.created_at
FROM users u
LEFT JOIN departments d ON u.department_id = d.id
LEFT JOIN positions p ON u.position_id = p.id
LEFT JOIN locations l ON u.location_id = l.id
WHERE (u.name ILIKE :search_term OR u.email ILIKE :search_term)
AND u.age >= :min_age AND u.age <= :max_age
AND d.name = :department
ORDER BY u.created_at DESC
```

### User Activity Summary
```sql
SELECT 
    u.name, u.email,
    COUNT(DISTINCT c.id) as total_courses,
    COUNT(DISTINCT CASE WHEN c.is_completed = true THEN c.id END) as completed_courses,
    AVG(c.progress) as avg_progress,
    COUNT(DISTINCT m.id) as total_modules,
    COUNT(DISTINCT CASE WHEN m.is_completed = true THEN m.id END) as completed_modules
FROM users u
LEFT JOIN courses c ON u.id = c.user_id
LEFT JOIN modules m ON c.id = m.course_id
WHERE u.id = :user_id
GROUP BY u.id, u.name, u.email
```

## Key Benefits of Raw SQL

### 1. Performance
- Direct database execution without ORM overhead
- Optimized query plans
- Reduced memory usage

### 2. Flexibility
- Complex queries that are difficult with ORM
- Database-specific functions and features
- Custom aggregations and calculations

### 3. Control
- Precise query optimization
- Custom indexing strategies
- Database-specific optimizations

## Best Practices

### 1. Parameterized Queries
Always use parameterized queries to prevent SQL injection:

```python
query = text("SELECT * FROM users WHERE email = :email")
result = db.execute(query, {'email': email})
```

### 2. Error Handling
Wrap database operations in try-catch blocks:

```python
try:
    result = db.execute(query, params)
    return result.fetchall()
except Exception as e:
    print(f"Database error: {e}")
    return []
```

### 3. Connection Management
Always close database connections:

```python
try:
    # Database operations
    pass
finally:
    repo.close()
```

### 4. Query Optimization
- Use appropriate indexes
- Limit result sets with pagination
- Use EXPLAIN to analyze query performance
- Avoid N+1 query problems

## Migration from ORM

To migrate from ORM-based queries to raw SQL:

1. **Identify Complex Queries**: Start with queries that are complex or slow with ORM
2. **Write Raw SQL**: Convert ORM queries to raw SQL
3. **Test Performance**: Compare performance between ORM and raw SQL
4. **Gradual Migration**: Migrate one query at a time
5. **Maintain Consistency**: Keep the same interface for easy switching

## Running the Examples

To run the example code:

```bash
cd /Users/gemaakbar/ionify/tara
python examples/raw_sql_usage.py
```

This will demonstrate various raw SQL operations and show the actual queries being executed.
