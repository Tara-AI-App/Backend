# Database Migrations Guide

This directory contains database migration files managed by Alembic. Migrations allow you to version control your database schema and apply changes safely across different environments.

## 📁 Directory Structure

```
alembic/
├── README.md                   # This file
├── env.py                      # Alembic environment configuration
├── script.py.mako              # Migration template
└── versions/                   # Migration files
    └── 2df45a588c13_initial_migration.py
```

## 🚀 Quick Start

### Prerequisites

Make sure you have installed the required dependencies:

```bash
pip install -r requirements/base.txt
```

### 1. Check Current Migration Status

```bash
# See current database revision
alembic current

# See all available revisions
alembic history --verbose
```

### 2. Apply Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply migrations up to a specific revision
alembic upgrade <revision_id>

# Apply one migration at a time
alembic upgrade +1
```

### 3. Create New Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Create empty migration for manual changes
alembic revision -m "Manual migration description"
```

## 📋 Common Commands

### Migration Management

| Command | Description |
|---------|-------------|
| `alembic current` | Show current database revision |
| `alembic history` | Show migration history |
| `alembic show <revision>` | Show specific revision details |
| `alembic heads` | Show latest revisions |
| `alembic branches` | Show branch points |

### Applying Migrations

| Command | Description |
|---------|-------------|
| `alembic upgrade head` | Apply all pending migrations |
| `alembic upgrade +1` | Apply next migration |
| `alembic upgrade <revision>` | Apply up to specific revision |
| `alembic upgrade <revision1>:<revision2>` | Apply between revisions |

### Rolling Back Migrations

| Command | Description |
|---------|-------------|
| `alembic downgrade -1` | Rollback one migration |
| `alembic downgrade <revision>` | Rollback to specific revision |
| `alembic downgrade base` | Rollback all migrations |

### Creating Migrations

| Command | Description |
|---------|-------------|
| `alembic revision --autogenerate -m "message"` | Auto-generate from models |
| `alembic revision -m "message"` | Create empty migration |
| `alembic merge -m "message" <revision1> <revision2>` | Merge branches |

## 🔧 Configuration

### Database URL

The database URL is configured in `alembic.ini`:

```ini
sqlalchemy.url = sqlite:///./tara.db
```

For different environments, you can override this:

```bash
# Use environment variable
export DATABASE_URL="postgresql://user:pass@localhost/tara"
alembic upgrade head

# Or specify in command
alembic -x url=postgresql://user:pass@localhost/tara upgrade head
```

### Environment Variables

You can set these environment variables to override configuration:

- `DATABASE_URL`: Database connection string
- `ALEMBIC_CONFIG`: Path to custom alembic.ini file

## 📝 Migration Workflow

### 1. Development Workflow

```bash
# 1. Make changes to your models in app/database/models.py
# 2. Generate migration
alembic revision --autogenerate -m "Add new field to Item model"

# 3. Review the generated migration file
# 4. Apply the migration
alembic upgrade head

# 5. Test your changes
python run.py
```

### 2. Production Deployment

```bash
# 1. Backup your database (IMPORTANT!)
pg_dump tara_production > backup.sql

# 2. Apply migrations
alembic upgrade head

# 3. Verify the changes
alembic current
```

### 3. Team Collaboration

```bash
# 1. Pull latest changes
git pull origin main

# 2. Apply new migrations
alembic upgrade head

# 3. Continue development
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Migration Conflicts

If you have migration conflicts:

```bash
# Check for conflicts
alembic branches

# Merge branches
alembic merge -m "Merge branches" <revision1> <revision2>
```

#### 2. Failed Migration

If a migration fails:

```bash
# Check current state
alembic current

# Rollback to previous state
alembic downgrade -1

# Fix the migration file and try again
alembic upgrade head
```

#### 3. Database Out of Sync

If your database is out of sync:

```bash
# Check what's different
alembic show head

# Force to specific revision (DANGEROUS!)
alembic stamp <revision>

# Then apply migrations
alembic upgrade head
```

### Debugging

#### Enable SQL Logging

Add this to your `alembic.ini`:

```ini
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = INFO
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

## 📊 Migration Best Practices

### 1. Naming Conventions

- Use descriptive names: `add_user_email_field`
- Include action: `add_`, `remove_`, `modify_`, `create_`
- Be specific: `add_user_email_index` not `add_index`

### 2. Migration Safety

- **Always backup** before applying migrations in production
- **Test migrations** on a copy of production data
- **Review auto-generated** migrations before applying
- **Use transactions** for complex migrations

### 3. Data Migrations

For data changes, create separate migrations:

```python
# In migration file
def upgrade():
    # Schema changes
    op.add_column('items', sa.Column('new_field', sa.String(255)))
    
    # Data migration
    connection = op.get_bind()
    connection.execute(
        "UPDATE items SET new_field = 'default_value' WHERE new_field IS NULL"
    )
```

### 4. Rollback Strategy

Always provide rollback logic:

```python
def upgrade():
    op.add_column('items', sa.Column('new_field', sa.String(255)))

def downgrade():
    op.drop_column('items', 'new_field')
```

## 🔍 Monitoring

### Check Migration Status

```bash
# Current revision
alembic current

# Pending migrations
alembic show head

# Migration history
alembic history --verbose
```

### Database Schema

```bash
# Show current schema
alembic show current

# Show specific revision
alembic show <revision_id>
```

## 🚨 Emergency Procedures

### Complete Rollback

```bash
# Rollback all migrations (DANGEROUS!)
alembic downgrade base

# Recreate database
python scripts/init_db.py
```

### Reset to Specific State

```bash
# Force database to specific revision
alembic stamp <revision_id>

# Apply migrations from that point
alembic upgrade head
```

## 📚 Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Database Migration Best Practices](https://www.prisma.io/dataguide/types/relational/what-are-database-migrations)

## 🆘 Getting Help

If you encounter issues:

1. Check the migration files in `versions/`
2. Review the Alembic logs
3. Verify your database connection
4. Check for syntax errors in migration files
5. Ensure all dependencies are installed

For more help, refer to the main project README.md or contact the development team.
