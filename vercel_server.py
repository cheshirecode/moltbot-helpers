"""
Vercel-compatible server for OpenClaw Demo

This adapts the Flask app for Vercel's serverless functions
Uses shared templates with the main dashboard
"""

from flask import Flask, jsonify, request
import random
from datetime import datetime, timedelta
import json
import sys
import os.path

# Add the project root to the path so we can import the renderer
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from templates.renderer import render_dashboard_for_demo_system

app = Flask(__name__)

# Generate synthetic project data for demo
def generate_demo_projects():
    """Generate synthetic project data for the demo."""
    project_names = [
        'openclaw-core', 'moltbot-integration', 'ai-automation', 'data-pipeline',
        'workflow-engine', 'knowledge-base', 'task-orchestration', 'sync-service'
    ]
    
    demo_projects = []
    for name in project_names:
        total_tasks = random.randint(15, 150)
        completed_tasks = random.randint(0, total_tasks)
        in_progress_tasks = random.randint(0, total_tasks - completed_tasks)
        todo_tasks = total_tasks - completed_tasks - in_progress_tasks
        
        demo_projects.append({
            'project': name,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'in_progress_tasks': in_progress_tasks,
            'todo_tasks': todo_tasks
        })
    
    return sorted(demo_projects, key=lambda x: x['total_tasks'], reverse=True)


def generate_demo_project_details(project_name):
    """Generate synthetic project details for demo."""
    # Possible values for demo data
    statuses = ['completed', 'in-progress', 'todo', 'blocked', 'review']
    priorities = ['critical', 'high', 'medium', 'low']
    categories = ['development', 'testing', 'documentation', 'research', 'maintenance', 'design']
    
    # Generate random counts
    total_tasks = random.randint(10, 50)
    
    # Generate status distribution
    status_counts = {}
    remaining = total_tasks
    for status in statuses[:-1]:  # Don't assign all to the last status
        if remaining <= 0:
            break
        count = random.randint(0, min(remaining, int(total_tasks * 0.4)))
        status_counts[status] = count
        remaining -= count
    # Assign remaining to last status
    status_counts[statuses[-1]] = remaining
    
    # Generate priority distribution
    priority_counts = {}
    remaining = total_tasks
    for priority in priorities[:-1]:
        if remaining <= 0:
            break
        count = random.randint(0, min(remaining, int(total_tasks * 0.3)))
        priority_counts[priority] = count
        remaining -= count
    priority_counts[priorities[-1]] = remaining
    
    # Generate category distribution
    category_counts = {}
    remaining = total_tasks
    for category in categories[:-1]:
        if remaining <= 0:
            break
        count = random.randint(0, min(remaining, int(total_tasks * 0.3)))
        category_counts[category] = count
        remaining -= count
    category_counts[categories[-1]] = remaining
    
    # Generate recent tasks
    recent_tasks = []
    for i in range(min(10, total_tasks)):
        recent_tasks.append({
            'id': random.randint(1000, 9999),
            'title': f'Demo task {i+1} for {project_name}',
            'status': random.choice(statuses),
            'priority': random.choice(priorities),
            'category': random.choice(categories),
            'created_date': (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d'),
            'updated_date': (datetime.now() - timedelta(days=random.randint(0, 14))).strftime('%Y-%m-%d'),
            'tags': ['demo', 'showcase', 'example']
        })
    
    return {
        "project": project_name,
        "statusCounts": status_counts,
        "priorityCounts": priority_counts,
        "categoryCounts": category_counts,
        "recentTasks": recent_tasks,
        "totalTasks": total_tasks
    }


@app.route('/')
def index():
    """Serve the demo landing page."""
    html_content = render_dashboard_for_demo_system()
    return html_content


@app.route('/api/demo/projects')
def get_demo_projects():
    """Get synthetic project data for demo."""
    try:
        projects = generate_demo_projects()
        return jsonify(projects)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/demo/project/<project_name>')
def get_demo_project_details(project_name):
    """Get synthetic project details for demo."""
    try:
        project_details = generate_demo_project_details(project_name)
        return jsonify(project_details)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/demo')
def demo_page():
    """Serve the demo dashboard page."""
    html_content = render_dashboard_for_demo_system()
    return html_content


# For Vercel deployment
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))