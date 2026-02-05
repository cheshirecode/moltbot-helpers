#!/usr/bin/env python3
"""
Task Management Dashboard API

Flask API to serve task data from PostgreSQL database to the UI
"""

from flask import Flask, jsonify, request, send_from_directory
import psycopg2
import os
from datetime import datetime, timedelta
import json

app = Flask(__name__, static_folder='.')

# Database connection parameters from environment variables
DB_HOST = os.environ.get("PT_DB_HOST", "localhost")
DB_PORT = int(os.environ.get("PT_DB_PORT", 5433))
DB_NAME = os.environ.get("PT_DB_NAME", "financial_analysis")
DB_USER = os.environ.get("PT_DB_USER", "finance_user")
DB_PASSWORD = os.environ.get("PT_DB_PASSWORD", "secure_finance_password")


def get_db_connection():
    """Get a connection to the PostgreSQL database."""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn


def get_projects_data():
    """Get list of all projects with task counts - standalone function."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get distinct projects with task counts
    cursor.execute("""
        SELECT 
            project,
            COUNT(*) as total_tasks,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_tasks,
            SUM(CASE WHEN status = 'in-progress' THEN 1 ELSE 0 END) as in_progress_tasks,
            SUM(CASE WHEN status = 'todo' OR status = 'new' THEN 1 ELSE 0 END) as todo_tasks
        FROM project_tracker
        GROUP BY project
        ORDER BY total_tasks DESC
    """)
    
    rows = cursor.fetchall()
    col_names = [desc[0] for desc in cursor.description]
    conn.close()
    
    projects = []
    for row in rows:
        # Convert tuple to dict using column names
        row_dict = {col_names[i]: row[i] for i in range(len(col_names))}
        projects.append(row_dict)
    
    return projects


@app.route('/')
def index():
    """Serve the main dashboard page."""
    return send_from_directory('.', 'dashboard.html')


@app.route('/api/projects')
def get_projects():
    """Get list of all projects with task counts."""
    try:
        projects = get_projects_data()
        return jsonify(projects)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/project/<project_name>')
def get_project_details(project_name):
    """Get detailed information for a specific project."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get task counts by status
        cursor.execute("""
            SELECT 
                status,
                COUNT(*) as count
            FROM project_tracker
            WHERE project = %s
            GROUP BY status
        """, (project_name,))
        
        status_rows = cursor.fetchall()
        status_counts = {row[0]: row[1] for row in status_rows}
        
        # Get task counts by priority
        cursor.execute("""
            SELECT 
                priority,
                COUNT(*) as count
            FROM project_tracker
            WHERE project = %s
            GROUP BY priority
        """, (project_name,))
        
        priority_rows = cursor.fetchall()
        priority_counts = {row[0]: row[1] for row in priority_rows}
        
        # Get task counts by category
        cursor.execute("""
            SELECT 
                category,
                COUNT(*) as count
            FROM project_tracker
            WHERE project = %s
            GROUP BY category
        """, (project_name,))
        
        category_rows = cursor.fetchall()
        category_counts = {row[0]: row[1] for row in category_rows}
        
        # Get recent tasks
        cursor.execute("""
            SELECT 
                id, title, status, priority, category, created_date, updated_date, tags
            FROM project_tracker
            WHERE project = %s
            ORDER BY updated_date DESC
            LIMIT 10
        """, (project_name,))
        
        recent_rows = cursor.fetchall()
        recent_col_names = [desc[0] for desc in cursor.description]
        
        recent_tasks = []
        for row in recent_rows:
            # Convert tuple to dict using column names
            row_dict = {recent_col_names[i]: row[i] for i in range(len(recent_col_names))}
            # Convert datetime objects to strings
            if isinstance(row_dict.get('created_date'), (datetime)):
                row_dict['created_date'] = row_dict['created_date'].isoformat()
            if isinstance(row_dict.get('updated_date'), (datetime)):
                row_dict['updated_date'] = row_dict['updated_date'].isoformat()
            # Convert tags from JSON string to object if needed
            if isinstance(row_dict.get('tags'), str):
                try:
                    row_dict['tags'] = json.loads(row_dict['tags'])
                except:
                    pass
            recent_tasks.append(row_dict)
        
        conn.close()
        
        # Calculate total tasks
        total_tasks = sum(status_counts.values())
        
        return jsonify({
            "project": project_name,
            "statusCounts": status_counts,
            "priorityCounts": priority_counts,
            "categoryCounts": category_counts,
            "recentTasks": recent_tasks,
            "totalTasks": total_tasks
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/stats')
def get_global_stats():
    """Get global statistics across all projects."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total task count
        cursor.execute("SELECT COUNT(*) FROM project_tracker")
        total_tasks = cursor.fetchone()[0]
        
        # Get status distribution
        cursor.execute("""
            SELECT status, COUNT(*) 
            FROM project_tracker 
            GROUP BY status
        """)
        status_distribution = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Get priority distribution
        cursor.execute("""
            SELECT priority, COUNT(*) 
            FROM project_tracker 
            GROUP BY priority
        """)
        priority_distribution = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Get project count
        cursor.execute("SELECT COUNT(DISTINCT project) FROM project_tracker")
        project_count = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            "totalTasks": total_tasks,
            "projectCount": project_count,
            "statusDistribution": status_distribution,
            "priorityDistribution": priority_distribution
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)