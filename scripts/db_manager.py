#!/usr/bin/env python3
"""
Database Management Script for Tara LMS
Provides easy commands to manage the database
"""

import sqlite3
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.database.connection import engine
from app.database.models import Base

def create_database():
    """Create all tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

def drop_database():
    """Drop all tables"""
    print("Dropping database tables...")
    Base.metadata.drop_all(bind=engine)
    print("✅ Database tables dropped successfully!")

def show_tables():
    """Show all tables in the database"""
    print("📊 Database Tables:")
    print("-" * 40)
    
    # Connect to SQLite database
    db_path = project_root / "tara.db"
    if not db_path.exists():
        print("❌ Database file not found!")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    for table in tables:
        print(f"📋 {table[0]}")
    
    conn.close()
    print(f"\nTotal tables: {len(tables)}")

def show_schema(table_name=None):
    """Show schema for a specific table or all tables"""
    db_path = project_root / "tara.db"
    if not db_path.exists():
        print("❌ Database file not found!")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    if table_name:
        print(f"📋 Schema for table '{table_name}':")
        print("-" * 50)
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        if not columns:
            print(f"❌ Table '{table_name}' not found!")
            return
        
        for col in columns:
            print(f"  {col[1]} {col[2]} {'NOT NULL' if col[3] else 'NULL'} {'PRIMARY KEY' if col[5] else ''}")
    else:
        print("📋 Database Schema:")
        print("-" * 50)
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
        schemas = cursor.fetchall()
        
        for schema in schemas:
            print(schema[0])
            print()
    
    conn.close()

def run_query(query):
    """Run a custom SQL query"""
    db_path = project_root / "tara.db"
    if not db_path.exists():
        print("❌ Database file not found!")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            # Get column names
            columns = [description[0] for description in cursor.description]
            print("📊 Query Results:")
            print("-" * 50)
            
            # Print column headers
            print(" | ".join(columns))
            print("-" * 50)
            
            # Print results
            for row in results:
                print(" | ".join(str(cell) for cell in row))
        else:
            print("✅ Query executed successfully (no results)")
            
    except sqlite3.Error as e:
        print(f"❌ Query error: {e}")
    finally:
        conn.close()

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("""
🗄️  Tara Database Manager

Usage:
    python scripts/db_manager.py <command> [options]

Commands:
    create          Create all database tables
    drop            Drop all database tables
    tables          Show all tables
    schema [table]  Show schema (all tables or specific table)
    query <sql>     Run custom SQL query

Examples:
    python scripts/db_manager.py create
    python scripts/db_manager.py tables
    python scripts/db_manager.py schema users
    python scripts/db_manager.py query "SELECT * FROM users LIMIT 5"
        """)
        return
    
    command = sys.argv[1].lower()
    
    if command == "create":
        create_database()
    elif command == "drop":
        drop_database()
    elif command == "tables":
        show_tables()
    elif command == "schema":
        table_name = sys.argv[2] if len(sys.argv) > 2 else None
        show_schema(table_name)
    elif command == "query":
        if len(sys.argv) < 3:
            print("❌ Please provide a SQL query")
            return
        query = " ".join(sys.argv[2:])
        run_query(query)
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()
