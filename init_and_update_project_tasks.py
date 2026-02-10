#!/usr/bin/env python3
"""
Script to initialize the project tracker database and update tasks to reflect 
the correct architecture: OpenClaw gateway runs in WSL for direct management, 
while PostgreSQL database runs in Kubernetes cluster.
"""

import os
import sys
import json
import psycopg2
import psycopg2.extras
from datetime import datetime

# PostgreSQL connection settings (same as pt/fp/seek tools)
DB_HOST = os.environ.get("PT_DB_HOST", "localhost")
DB_PORT = int(os.environ.get("PT_DB_PORT", 5433))
DB_NAME = os.environ.get("PT_DB_NAME", "financial_analysis")
DB_USER = os.environ.get("PT_DB_USER", "finance_user")
DB_PASSWORD = os.environ.get("PT_DB_PASSWORD", "secure_finance_password")

def get_connection():
    """Establish a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        sys.exit(1)

def init_database():
    """Initialize the database with the correct schema."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create the project_tracker table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_tracker (
            id SERIAL PRIMARY KEY,
            project TEXT NOT NULL,
            category TEXT,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT DEFAULT 'medium',
            impact TEXT,
            tech_debt_level TEXT,
            status TEXT DEFAULT 'new',
            created_date TIMESTAMP,
            updated_date TIMESTAMP,
            tags JSONB
        )
    """)
    
    conn.commit()
    conn.close()
    print("Database initialized with project_tracker table.")

def list_entries(conn, project="openclaw"):
    """List all entries for the openclaw project."""
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("""
        SELECT * FROM project_tracker 
        WHERE project = %s 
        ORDER BY created_date DESC, priority ASC NULLS LAST
    """, (project,))
    
    rows = cursor.fetchall()
    print(f"Entries for project '{project}':")
    print("-" * 80)
    for row in rows:
        print(f"ID: {row['id']}")
        print(f"Category: {row['category']}")
        print(f"Priority: {row['priority']}")
        print(f"Status: {row['status']}")
        print(f"Title: {row['title']}")
        print(f"Description: {row['description'][:100] if row['description'] else ''}{'...' if row['description'] and len(row['description']) > 100 else ''}")
        print(f"Tags: {row['tags']}")
        print(f"Created: {row['created_date']}, Updated: {row['updated_date']}")
        print("-" * 80)
    
    return rows

def insert_correct_architecture_tasks(conn):
    """Insert tasks that correctly reflect the WSL gateway + K8s DB architecture."""
    cursor = conn.cursor()
    
    # Get current date for timestamps
    now_str = datetime.now()
    
    # Define the correct architecture tasks
    correct_architecture_tasks = [
        {
            "category": "roadmap",
            "title": "OpenClaw gateway runs in WSL for direct management",
            "description": "Implement OpenClaw gateway to run in WSL environment for direct system management and control.",
            "priority": "high",
            "status": "new",
            "tags": ["architecture", "gateway", "wsl"]
        },
        {
            "category": "roadmap", 
            "title": "PostgreSQL database runs in Kubernetes cluster",
            "description": "Deploy PostgreSQL database in Kubernetes cluster for scalability and resilience, managed separately from gateway.",
            "priority": "high",
            "status": "new",
            "tags": ["architecture", "database", "kubernetes", "postgresql"]
        },
        {
            "category": "roadmap",
            "title": "Configure WSL-K8s communication for OpenClaw",
            "description": "Set up secure communication between WSL-based OpenClaw gateway and PostgreSQL in Kubernetes cluster.",
            "priority": "medium", 
            "status": "new",
            "tags": ["networking", "communication", "configuration"]
        },
        {
            "category": "roadmap",
            "title": "Implement hybrid deployment strategy",
            "description": "Create deployment scripts and documentation for the hybrid approach: gateway in WSL, DB in K8s.",
            "priority": "medium",
            "status": "new", 
            "tags": ["deployment", "documentation", "hybrid"]
        }
    ]
    
    # Insert the tasks
    for task in correct_architecture_tasks:
        cursor.execute("""
            INSERT INTO project_tracker (
                project, category, title, description, priority, status,
                created_date, updated_date, tags
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            "openclaw", 
            task["category"],
            task["title"], 
            task["description"],
            task["priority"],
            task["status"],
            now_str,  # created_date
            now_str,  # updated_date
            json.dumps(task["tags"]) # Convert tags list to JSONB string
        ))
        print(f"Added new task: {task['title']}")
    
    conn.commit()
    print(f"\nAdded {len(correct_architecture_tasks)} tasks reflecting the correct architecture (WSL gateway + K8s DB).")

def main():
    print("Initializing project tracker database...")
    init_database()
    
    conn = get_connection()
    
    print("\nCurrent project entries:")
    entries = list_entries(conn)
    
    print(f"\nTotal entries found: {len(entries)}")
    
    print("\nAdding tasks that reflect the correct architecture (WSL gateway + K8s DB)...")
    insert_correct_architecture_tasks(conn)
    
    print("\nUpdated project entries:")
    list_entries(conn)
    
    conn.close()
    print("\nDatabase updated successfully!")

if __name__ == "__main__":
    main()