#!/usr/bin/env python3
"""
Script to add a task explaining that the previous Docker-only execution tasks (IDs 284-288) 
were invalid based on current requirements and documenting the correct architecture.
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

def add_invalid_tasks_documentation():
    """Add a task documenting that previous Docker-only tasks were invalid."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get current date for timestamp
    now_str = datetime.now() # Use datetime object for TIMESTAMP column
    
    # Add documentation task about invalid previous tasks
    invalid_task_doc = {
        "category": "documentation",
        "title": "Invalid: Previous Docker-only execution tasks (IDs 284-288) are obsolete",
        "description": "Previous tasks 284-288 describing Docker-only execution approach are invalid based on current requirements. Correct architecture is hybrid: OpenClaw gateway runs in WSL for direct management, while PostgreSQL database runs in Kubernetes cluster. This hybrid approach provides better performance and management capabilities compared to the previous Docker-only approach.",
        "priority": "medium",
        "status": "completed",
        "tags": ["invalid", "tasks", "documentation", "architecture", "hybrid"] # Tags as a list
    }
    
    cursor.execute("""
        INSERT INTO project_tracker (
            project, category, title, description, priority, status,
            created_date, updated_date, tags
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        "openclaw", 
        invalid_task_doc["category"],
        invalid_task_doc["title"], 
        invalid_task_doc["description"],
        invalid_task_doc["priority"],
        invalid_task_doc["status"],
        now_str,  # created_date
        now_str,  # updated_date
        json.dumps(invalid_task_doc["tags"]) # Convert tags list to JSONB string
    ))
    
    print(f"Added documentation task: {invalid_task_doc['title']}")
    
    conn.commit()
    conn.close()
    print("\nDocumentation task added successfully!")

def main():
    print("Adding documentation about invalid previous tasks...")
    add_invalid_tasks_documentation()
    
    # Verify the addition
    print("\nVerifying the new documentation task was added:")
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) # Use RealDictCursor for dict-like access
    cursor.execute("""
        SELECT * FROM project_tracker 
        WHERE project = %s
        AND title ILIKE %s
        ORDER BY created_date DESC
    """, (
        'openclaw',
        '%Invalid: Previous Docker-only execution tasks%' # Use ILIKE for case-insensitive search
    ))
    
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row['id']}")
        print(f"Category: {row['category']}")
        print(f"Priority: {row['priority']}")
        print(f"Status: {row['status']}")
        print(f"Title: {row['title']}")
        print(f"Description: {row['description'][:200]}...")
        print(f"Tags: {row['tags']}")
        print("-" * 80)
    
    conn.close()

if __name__ == "__main__":
    main()