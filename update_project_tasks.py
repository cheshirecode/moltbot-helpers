#!/usr/bin/env python3
"""
Script to update project tracker tasks to reflect the correct architecture:
OpenClaw gateway runs in WSL for direct management, while PostgreSQL database 
runs in Kubernetes cluster.
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

def update_task_architecture(conn):
    """Update tasks to reflect the correct architecture: WSL gateway + K8s DB."""
    cursor = conn.cursor()
    
    # Get current date for updating timestamps
    now_str = datetime.now()
    
    # First, let's identify the incorrect Docker-only execution tasks 
    # Search for tasks that mention Docker execution or similar
    cursor.execute("""
        SELECT id, title, description 
        FROM project_tracker 
        WHERE project = %s 
        AND (title ILIKE %s OR description ILIKE %s 
             OR title ILIKE %s OR description ILIKE %s
             OR title ILIKE %s OR description ILIKE %s)
    """, ('openclaw', '%Docker%', '%Docker%', '%execution%', '%execution%', '%container%', '%container%'))
    
    docker_related_tasks = cursor.fetchall()
    print(f"Found {len(docker_related_tasks)} potentially Docker-related tasks to update/review:")
    for task_row in docker_related_tasks: # Renamed 'task' to 'task_row' to avoid conflict with task dictionary later
        print(f"  - ID {task_row['id']}: {task_row['title']}")
    
    # Update existing tasks that incorrectly describe the architecture
    update_count = 0
    
    # Example update for any tasks that describe incorrect Docker-only architecture
    cursor.execute("""
        UPDATE project_tracker 
        SET description = REPLACE(description, 'Docker-only execution', 'hybrid execution with WSL gateway and K8s DB'),
            updated_date = %s
        WHERE project = %s 
        AND description ILIKE %s
    """, (now_str, 'openclaw', '%Docker-only%'))
    update_count += cursor.rowcount
    
    cursor.execute("""
        UPDATE project_tracker 
        SET description = REPLACE(description, 'runs in Docker containers', 'gateway runs in WSL, database runs in Kubernetes'),
            updated_date = %s
        WHERE project = %s 
        AND description ILIKE %s
    """, (now_str, 'openclaw', '%runs in Docker containers%'))
    update_count += cursor.rowcount
    
    # Now add the correct architecture tasks if they don't exist
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
    
    # Check if these tasks already exist to avoid duplicates
    for task in correct_architecture_tasks:
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM project_tracker 
            WHERE project = %s 
            AND title = %s
        """, ('openclaw', task["title"]))
        
        result = cursor.fetchone()
        if result[0] == 0:  # Use result[0] for count from fetchone()
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
        else:
            print(f"Task already exists: {task['title']}")
    
    conn.commit()
    print(f"\nUpdated {update_count} existing tasks to reflect correct architecture.")
    print(f"Added new tasks reflecting the correct architecture (WSL gateway + K8s DB).")

def main():
    print("Connecting to project tracker database...")
    
    try:
        conn = get_connection()
        
        print("\nCurrent project entries:")
        entries = list_entries(conn)
        
        print(f"\nTotal entries found: {len(entries)}")
        
        print("\nUpdating tasks to reflect correct architecture (WSL gateway + K8s DB)...")
        update_task_architecture(conn)
        
        print("\nUpdated project entries:")
        list_entries(conn)
        
        conn.close()
        print("\nDatabase updated successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()