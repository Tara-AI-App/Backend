#!/usr/bin/env python3
"""
Migration script with environment-specific database configuration
"""
import os
import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.config import settings

def run_migration(command="upgrade head", database_url=None):
    """Run alembic migration with specific database URL"""
    
    # Use provided URL or default from settings
    db_url = database_url or settings.DATABASE_URL
    
    # Set environment variable
    env = os.environ.copy()
    env['DATABASE_URL'] = db_url
    
    # Run alembic command
    cmd = ['alembic'] + command.split()
    print(f"Running: {' '.join(cmd)}")
    print(f"Database: {db_url}")
    
    result = subprocess.run(cmd, env=env, cwd=project_root)
    return result.returncode

def main():
    """Main migration function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run database migrations')
    parser.add_argument('command', nargs='?', default='upgrade head', 
                       help='Alembic command (default: upgrade head)')
    parser.add_argument('--db', '--database', 
                       help='Database URL override')
    parser.add_argument('--env', choices=['dev', 'test', 'prod'],
                       help='Environment preset')
    
    args = parser.parse_args()
    
    # Environment presets
    if args.env:
        if args.env == 'dev':
            db_url = "sqlite:///./tara_dev.db"
        elif args.env == 'test':
            db_url = "sqlite:///./tara_test.db"
        elif args.env == 'prod':
            db_url = "postgresql://user:password@localhost/tara_prod"
    else:
        db_url = args.db
    
    # Run migration
    exit_code = run_migration(args.command, db_url)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
