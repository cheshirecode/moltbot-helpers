#!/usr/bin/env python3
"""
Public Demo Dashboard API

Flask API to serve synthetic demo data for public showcase
"""

from flask import Flask, jsonify, request, send_from_directory
import random
from datetime import datetime, timedelta
import json

app = Flask(__name__, static_folder='.')

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


def generate_demo_task_details(project_name, task_id):
    """Generate synthetic task details for demo."""
    # This is a simplified version for demo purposes
    # In a real system, you would fetch this from a database
    return {
        "id": task_id,
        "project": project_name,
        "title": f"Demo Task {task_id} for {project_name}",
        "description": f"This is a synthetic description for Demo Task {task_id} in project {project_name}.",
        "status": random.choice(['todo', 'in-progress', 'completed', 'blocked', 'review']),
        "priority": random.choice(['critical', 'high', 'medium', 'low']),
        "category": random.choice(['development', 'testing', 'documentation', 'research', 'maintenance', 'design']),
        "created_date": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d'),
        "updated_date": (datetime.now() - timedelta(days=random.randint(0, 14))).strftime('%Y-%m-%d')
    }


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
    """Serve a demo landing page."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>OpenClaw Demo Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            :root {
                --primary-color: #4361ee;
                --secondary-color: #3f37c9;
                --success-color: #4cc9f0;
                --warning-color: #f72585;
                --light-bg: #f8f9fa;
                --dark-text: #212529;
                --border-color: #dee2e6;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f7fb;
                color: var(--dark-text);
                line-height: 1.6;
            }
            
            .container {
                max-width: 1400px;
                margin: 0 auto;
            }
            
            header {
                text-align: center;
                margin-bottom: 30px;
                padding: 20px;
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            
            h1 {
                margin: 0;
                font-size: 2.5rem;
            }
            
            .subtitle {
                font-size: 1.2rem;
                opacity: 0.9;
                margin-top: 10px;
            }
            
            .intro {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                margin-bottom: 30px;
                text-align: center;
            }
            
            .controls {
                display: flex;
                gap: 15px;
                margin-bottom: 20px;
                flex-wrap: wrap;
                align-items: center;
            }
            
            select, button {
                padding: 10px 15px;
                border: 1px solid var(--border-color);
                border-radius: 5px;
                font-size: 1rem;
            }
            
            button {
                background-color: var(--primary-color);
                color: white;
                cursor: pointer;
                border: none;
            }
            
            button:hover {
                background-color: var(--secondary-color);
            }
            
            .dashboard-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .card {
                background: white;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                transition: transform 0.2s;
            }
            
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            
            .card-title {
                font-size: 1.2rem;
                font-weight: 600;
                margin: 0 0 15px 0;
                color: var(--primary-color);
                border-bottom: 2px solid var(--light-bg);
                padding-bottom: 10px;
            }
            
            .chart-container {
                position: relative;
                height: 300px;
                margin: 20px 0;
            }
            
            .project-list {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                gap: 15px;
            }
            
            .project-card {
                background: white;
                border-radius: 8px;
                padding: 15px;
                border-left: 4px solid var(--primary-color);
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            }
            
            .project-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }
            
            .project-name {
                font-weight: 600;
                font-size: 1.1rem;
                color: var(--secondary-color);
            }
            
            .task-count {
                background: var(--success-color);
                color: white;
                padding: 3px 8px;
                border-radius: 12px;
                font-size: 0.9rem;
            }
            
            .progress-bar {
                width: 100%;
                height: 8px;
                background-color: #e9ecef;
                border-radius: 4px;
                overflow: hidden;
                margin: 10px 0;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, var(--success-color), var(--primary-color));
                border-radius: 4px;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }
            
            .stat-card {
                background: white;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            }
            
            .stat-value {
                font-size: 2rem;
                font-weight: 700;
                color: var(--primary-color);
            }
            
            .stat-label {
                font-size: 0.9rem;
                color: #6c757d;
            }
            
            .disclaimer {
                background: #fff3cd;
                color: #856404;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                border-left: 4px solid #ffc107;
            }
            
            .loading {
                text-align: center;
                padding: 40px;
                font-size: 1.2rem;
                color: #6c757d;
            }
            
            .error {
                background: #f8d7da;
                color: #721c24;
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
            }

            .task-board-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
            }

            .task-column {
                background: var(--light-bg);
                border-radius: 8px;
                padding: 15px;
                min-height: 200px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                border: 1px solid var(--border-color);
            }

            .task-column h4 {
                text-align: center;
                margin-top: 0;
                margin-bottom: 15px;
                color: var(--primary-color);
                padding-bottom: 10px;
                border-bottom: 1px solid var(--border-color);
            }

            .task-list {
                min-height: 100px; /* Ensure drop target is visible */
            }

            .task-item {
                background: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                margin-bottom: 10px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                cursor: grab;
            }

            .task-item:active {
                cursor: grabbing;
            }
        
            .task-item.dragging {
                opacity: 0.5;
            }
            
            @media (max-width: 768px) {
                .controls {
                    flex-direction: column;
                    align-items: stretch;
                }
                
                .dashboard-grid {
                    grid-template-columns: 1fr;
                }

                .task-board-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>OpenClaw Demo Dashboard</h1>
                <div class="subtitle">Showcasing task management capabilities</div>
            </header>
            
            <div class="disclaimer">
                <strong>Note:</strong> This is a demonstration system using synthetic data. 
                The actual OpenClaw system operates independently with real data.
            </div>
            
            <div class="intro">
                <h2>Welcome to the OpenClaw Demo</h2>
                <p>This dashboard showcases the task management capabilities of the OpenClaw system.</p>
                <p>All data shown here is synthetic and generated for demonstration purposes only.</p>
            </div>
            
            <div class="controls">
                <select id="projectSelect">
                    <option value="">Select a demo project...</option>
                </select>
                <button onclick="loadProjectData()">Load Project Data</button>
                <button onclick="loadAllProjects()">Load All Projects</button>
            </div>
            
            <div id="loadingIndicator" class="loading" style="display: none;">
                Loading demo data...
            </div>
            
            <div id="errorMessage" class="error" style="display: none;"></div>
            
            <div id="dashboardContent" style="display: none;">
                <div class="stats-grid" id="statsGrid">
                    <!-- Stats will be populated here -->
                </div>
                
                <div class="dashboard-grid">
                    <div class="card">
                        <h3 class="card-title">Tasks by Status</h3>
                        <div class="chart-container">
                            <canvas id="statusChart"></canvas>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3 class="card-title">Tasks by Priority</h3>
                        <div class="chart-container">
                            <canvas id="priorityChart"></canvas>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3 class="card-title">Tasks by Category</h3>
                        <div class="chart-container">
                            <canvas id="categoryChart"></canvas>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h3 class="card-title">Activity Heat Map</h3>
                    <div id="activityHeatMap"></div>
                </div>
                
                <div class="card">
                    <h3 class="card-title">Burn-down Chart</h3>
                    <div class="chart-container">
                        <canvas id="burndownChart"></canvas>
                    </div>
                </div>
                
                <div class="card">
                    <h3 class="card-title">Timeline View</h3>
                    <div id="timelineContainer" style="overflow-x: auto; padding: 10px;">
                        <div id="timelineChart" style="min-width: 800px; height: 300px;"></div>
                    </div>
                </div>
                
                <div class="card">
                    <h3 class="card-title">Task Board</h3>
                    <div class="task-board-grid">
                        <div class="task-column" id="todo-column" data-status="todo">
                            <h4>To Do</h4>
                            <div class="task-list" id="todoTasks"></div>
                        </div>
                        <div class="task-column" id="in-progress-column" data-status="in-progress">
                            <h4>In Progress</h4>
                            <div class="task-list" id="inProgressTasks"></div>
                        </div>
                        <div class="task-column" id="completed-column" data-status="completed">
                            <h4>Completed</h4>
                            <div class="task-list" id="completedTasks"></div>
                        </div>
                        <div class="task-column" id="blocked-column" data-status="blocked">
                            <h4>Blocked</h4>
                            <div class="task-list" id="blockedTasks"></div>
                        </div>
                        <div class="task-column" id="review-column" data-status="review">
                            <h4>Review</h4>
                            <div class="task-list" id="reviewTasks"></div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div id="allProjectsView" style="display: none;">
                <h2 class="card-title">All Projects Overview</h2>
                <div class="project-list" id="projectListView">
                    <!-- Project cards will be populated here -->
                </div>
            </div>
        </div>

        <script src="/shared-dashboard.js"></script>
        <script>
            // Initialize the demo dashboard with appropriate configuration
            document.addEventListener('DOMContentLoaded', function() {
                const dashboard = new OpenClawDashboard({
                    isDemoMode: true,
                    apiBaseUrl: '/api/demo',
                    title: 'OpenClaw Demo Dashboard',
                    subtitle: 'Showcasing task management capabilities',
                    showDisclaimer: true,
                    demoDisclaimer: 'This is a demonstration system using synthetic data. The actual OpenClaw system operates independently with real data.',
                    features: {
                        refreshButton: false, // Hide refresh button in demo mode
                        loadingIndicator: true,
                        errorHandling: true,
                        projectSelection: true,
                        allProjectsView: true,
                        interactiveTasks: true,  // Enable interactive task management (for demo purposes)
                        taskEditing: true,       // Enable task editing (for demo purposes)
                        taskCreation: false,     // Disable task creation in demo mode
                        dragAndDrop: false,      // Disable drag-and-drop in demo mode
                        timeTracking: true,      // Enable time tracking (for demo purposes)
                        timelineView: true,      // Enable timeline view (for demo purposes)
                        assignmentTracking: true, // Enable assignment tracking (for demo purposes)
                        tagsLabeling: true,      // Enable tags and labeling (for demo purposes)
                        dependencyTracking: true, // Enable dependency tracking (for demo purposes)
                        taskBreakdowns: true,    // Enable task breakdowns/subtasks (for demo purposes)
                        burndownChart: true,     // Enable burn-down chart (for demo purposes)
                        activityHeatMap: true    // Enable activity heat map (for demo purposes)
                    }
                });
                
                window.demoDashboard = dashboard;
                dashboard.initialize();
            });
        </script>
    </body>
    </html>
    """
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


@app.route('/api/demo/project/<project_name>/task/<task_id>', methods=['PUT'])
def update_demo_task_status(project_name, task_id):
    """Update task status in demo mode (simulated)."""
    try:
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({"error": "Status is required"}), 400
        
        new_status = data['status']
        updated_date = data.get('updated_date', datetime.now().strftime('%Y-%m-%d'))
        
        # In demo mode, we just simulate the update and return success
        # In a real implementation, this would update the database
        
        return jsonify({
            "message": f"Task {task_id} status updated to {new_status}",
            "task_id": task_id,
            "new_status": new_status,
            "updated_date": updated_date
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/demo/project/<project_name>/task/<task_id>', methods=['GET'])
def get_demo_task_details(project_name, task_id):
    """Get synthetic task details for demo."""
    try:
        task_details = generate_demo_task_details(project_name, task_id)
        if not task_details:
            return jsonify({"error": "Task not found"}), 404
        return jsonify(task_details)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/demo/project/<project_name>/task', methods=['POST'])
def create_demo_task(project_name):
    """Simulate creating a new task in demo mode."""
    try:
        data = request.get_json()
        
        required_fields = ['title', 'description', 'status', 'priority', 'category']
        if not all(field in data for field in required_fields):
            return jsonify({"error": f"Missing required fields: {', '.join(required_fields)}"}), 400
        
        # Simulate successful task creation
        new_task_id = random.randint(10000, 99999)
        
        return jsonify({
            "message": "Demo task created successfully",
            "task_id": new_task_id,
            "project": project_name
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/shared-dashboard.js')
def serve_shared_dashboard_js():
    """Serve the shared dashboard JavaScript file."""
    # Read the shared dashboard JS file from the current directory
    try:
        with open('shared-dashboard.js', 'r') as f:
            js_content = f.read()
        return js_content, 200, {'Content-Type': 'application/javascript'}
    except FileNotFoundError:
        return "Shared dashboard file not found", 404


@app.route('/demo')
def demo_page():
    """Serve the demo dashboard page."""
    return index()


def main():
    print("🚀 Starting OpenClaw Public Demo Server...")
    print("🌐 Demo available at: http://localhost:5001/demo")
    print("🔐 This is a completely isolated demo system")
    print("🔒 No connection to main OpenClaw system")
    app.run(debug=True, host='0.0.0.0', port=5001)


if __name__ == '__main__':
    main()