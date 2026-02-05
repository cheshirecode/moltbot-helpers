"""
Vercel API Routes for OpenClaw Demo Dashboard with PostgreSQL-to-IndexedDB Mirror
"""

import json
import random
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
import os

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


def generate_postgresql_schema():
    """Generate PostgreSQL schema for IndexedDB auto-generation."""
    schema = {
        "project_tracker": {
            "primary_key": "id",
            "columns": [
                {"name": "id", "type": "integer", "is_nullable": False, "is_primary_key": True},
                {"name": "project", "type": "varchar", "is_nullable": False, "is_indexed": True},
                {"name": "title", "type": "varchar", "is_nullable": False},
                {"name": "description", "type": "text", "is_nullable": True},
                {"name": "status", "type": "varchar", "is_nullable": True, "is_indexed": True},
                {"name": "priority", "type": "varchar", "is_nullable": True, "is_indexed": True},
                {"name": "category", "type": "varchar", "is_nullable": True, "is_indexed": True},
                {"name": "created_date", "type": "timestamp", "is_nullable": True, "is_indexed": True},
                {"name": "updated_date", "type": "timestamp", "is_nullable": True, "is_indexed": True},
                {"name": "tags", "type": "jsonb", "is_nullable": True}
            ]
        }
    }
    
    return schema


def generate_indexeddb_setup_code(schema):
    """Generate JavaScript code for IndexedDB setup based on PostgreSQL schema."""
    js_lines = [
        "// Auto-generated IndexedDB setup from PostgreSQL schema",
        "function setupIndexedDB(dbVersion = 1) {",
        "  return new Promise((resolve, reject) => {",
        "    const request = indexedDB.open('openclaw_mirror', dbVersion);",
        "",
        "    request.onerror = () => reject(request.error);",
        "    request.onsuccess = () => resolve(request.result);",
        "",
        "    request.onupgradeneeded = (event) => {",
        "      const db = event.target.result;"
    ]
    
    for table_name, table_def in schema.items():
        key_path = table_def.get('primary_key', 'id')
        js_lines.extend([
            f"      if (!db.objectStoreNames.contains('{table_name}')) {{",
            f"        const store = db.createObjectStore('{table_name}', {{ keyPath: '{key_path}' }});"
        ])
        
        for col in table_def.get('columns', []):
            if col.get('is_indexed') or col['name'] in ['status', 'priority', 'category', 'project']:
                js_lines.append(f"        store.createIndex('{col['name']}', '{col['name']}', {{ unique: false }});")
        
        js_lines.append("      }")
    
    js_lines.extend([
        "    };",
        "  });",
        "}"
    ])
    
    return '\n'.join(js_lines)


def generate_dashboard_html():
    """Generate the dashboard HTML with embedded JavaScript for PostgreSQL-to-IndexedDB mirror."""
    return """
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
        
        .indexeddb-section {
            background: #e8f4fd;
            border: 1px solid #b6d7ff;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        
        .indexeddb-code {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 15px;
            font-family: monospace;
            white-space: pre-wrap;
            overflow-x: auto;
            margin: 10px 0;
        }
        
        .feature-highlight {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 5px;
            padding: 15px;
            margin: 15px 0;
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
        
        <div class="feature-highlight">
            <h3>🚀 Innovation: PostgreSQL-to-IndexedDB Mirror System</h3>
            <p>This demo includes an auto-generated IndexedDB schema based on PostgreSQL structure, enabling offline capability and faster UI performance.</p>
        </div>
        
        <div class="controls">
            <select id="projectSelect">
                <option value="">Select a demo project...</option>
            </select>
            <button onclick="loadProjectData()">Load Project Data</button>
            <button onclick="loadAllProjects()">Load All Projects</button>
            <button onclick="generateIndexedDBSchema()">Generate IndexedDB Schema</button>
        </div>
        
        <div id="loadingIndicator" class="loading" style="display: none;">
            Loading data...
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
                <h3 class="card-title">Recent Tasks</h3>
                <div id="recentTasksList">
                    <!-- Recent tasks will be populated here -->
                </div>
            </div>
        </div>
        
        <div id="allProjectsView" style="display: none;">
            <h2 class="card-title">All Projects Overview</h2>
            <div class="project-list" id="projectListView">
                <!-- Project cards will be populated here -->
            </div>
        </div>
        
        <div id="indexedDBSection" class="indexeddb-section" style="display: none;">
            <h3>🔧 PostgreSQL-to-IndexedDB Mirror</h3>
            <p>Auto-generated IndexedDB schema based on PostgreSQL structure:</p>
            <div id="indexedDBCode" class="indexeddb-code"></div>
            <p>This enables offline capability and faster UI performance by storing data locally in the browser.</p>
        </div>
    </div>

    <script>
        // Global variables to hold chart instances
        let statusChart = null;
        let priorityChart = null;
        let categoryChart = null;
        
        // Initialize the dashboard
        document.addEventListener('DOMContentLoaded', function() {
            initializeDashboard();
        });
        
        async function initializeDashboard() {
            try {
                // Load all projects view by default
                await loadAllProjects();
            } catch (error) {
                console.error('Error initializing dashboard:', error);
            }
        }
        
        async function loadAllProjects() {
            try {
                // Fetch demo projects data
                const response = await fetch('/api/demo/projects');
                if (!response.ok) {
                    throw new Error(`API error: ${response.status} ${response.statusText}`);
                }
                const projects = await response.json();
                
                // Populate project selector
                populateProjectSelector(projects.map(p => p.project));
                
                // Display all projects
                displayAllProjects(projects);
                
                document.getElementById('allProjectsView').style.display = 'block';
                document.getElementById('dashboardContent').style.display = 'none';
            } catch (error) {
                console.error('Error loading all projects:', error);
                showError('Error loading projects: ' + error.message);
            }
        }
        
        function populateProjectSelector(projects) {
            const select = document.getElementById('projectSelect');
            select.innerHTML = '<option value="">Select a demo project...</option>';
            
            projects.forEach(project => {
                const option = document.createElement('option');
                option.value = project;
                option.textContent = project;
                select.appendChild(option);
            });
        }
        
        async function loadProjectData() {
            const selectedProject = document.getElementById('projectSelect').value;
            
            if (!selectedProject) {
                showError('Please select a project first');
                return;
            }
            
            try {
                // Fetch demo project details
                const response = await fetch('/api/demo/project/' + encodeURIComponent(selectedProject));
                if (!response.ok) {
                    throw new Error(`API error: ${response.status} ${response.statusText}`);
                }
                const projectData = await response.json();
                
                displayProjectData(projectData);
                
                document.getElementById('dashboardContent').style.display = 'block';
                document.getElementById('allProjectsView').style.display = 'none';
            } catch (error) {
                console.error('Error loading project data:', error);
                showError('Error loading project data: ' + error.message);
            }
        }
        
        function showError(message) {
            const errorDiv = document.getElementById('errorMessage');
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            
            setTimeout(() => {
                errorDiv.style.display = 'none';
            }, 5000);
        }
        
        function showLoading(show) {
            document.getElementById('loadingIndicator').style.display = show ? 'block' : 'none';
        }
        
        function displayProjectData(data) {
            // Update stats
            updateStats([
                { label: 'Total Tasks', value: data.totalTasks },
                { label: 'Status Types', value: Object.keys(data.statusCounts).length },
                { label: 'Priority Levels', value: Object.keys(data.priorityCounts).length },
                { label: 'Categories', value: Object.keys(data.categoryCounts).length }
            ]);
            
            // Create/update charts
            createOrUpdateChart('statusChart', 'bar', 'Tasks by Status', data.statusCounts);
            createOrUpdateChart('priorityChart', 'doughnut', 'Tasks by Priority', data.priorityCounts);
            createOrUpdateChart('categoryChart', 'bar', 'Tasks by Category', data.categoryCounts);
            
            // Display recent tasks
            displayRecentTasks(data.recentTasks);
        }
        
        function displayAllProjects(projectsData) {
            const container = document.getElementById('projectListView');
            container.innerHTML = '';
            
            projectsData.forEach(project => {
                const progressPercent = project.completed_tasks > 0 ? 
                    Math.round((project.completed_tasks / project.total_tasks) * 100) : 0;
                
                const projectCard = document.createElement('div');
                projectCard.className = 'project-card';
                projectCard.innerHTML = `
                    <div class="project-header">
                        <div class="project-name">${project.project}</div>
                        <div class="task-count">${project.total_tasks}</div>
                    </div>
                    <div>Total Tasks: ${project.total_tasks}</div>
                    <div>Completed: ${project.completed_tasks}</div>
                    <div>In Progress: ${project.in_progress_tasks}</div>
                    <div>To Do: ${project.todo_tasks}</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${progressPercent}%"></div>
                    </div>
                    <div>${progressPercent}% Complete</div>
                `;
                
                container.appendChild(projectCard);
            });
        }
        
        function updateStats(stats) {
            const container = document.getElementById('statsGrid');
            container.innerHTML = '';
            
            stats.forEach(stat => {
                const statCard = document.createElement('div');
                statCard.className = 'stat-card';
                statCard.innerHTML = `
                    <div class="stat-value">${stat.value}</div>
                    <div class="stat-label">${stat.label}</div>
                `;
                container.appendChild(statCard);
            });
        }
        
        function createOrUpdateChart(canvasId, chartType, title, dataObj) {
            const ctx = document.getElementById(canvasId).getContext('2d');
            const labels = Object.keys(dataObj);
            const data = Object.values(dataObj);
            
            // Destroy existing chart if it exists
            const existingChart = Chart.getChart(canvasId);
            if (existingChart) {
                existingChart.destroy();
            }
            
            const chart = new Chart(ctx, {
                type: chartType,
                data: {
                    labels: labels,
                    datasets: [{
                        label: title,
                        data: data,
                        backgroundColor: [
                            'rgba(67, 97, 238, 0.7)',
                            'rgba(76, 201, 240, 0.7)',
                            'rgba(247, 37, 133, 0.7)',
                            'rgba(63, 55, 201, 0.7)',
                            'rgba(118, 89, 171, 0.7)',
                            'rgba(25, 118, 210, 0.7)'
                        ],
                        borderColor: [
                            'rgba(67, 97, 238, 1)',
                            'rgba(76, 201, 240, 1)',
                            'rgba(247, 37, 133, 1)',
                            'rgba(63, 55, 201, 1)',
                            'rgba(118, 89, 171, 1)',
                            'rgba(25, 118, 210, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: title
                        },
                        legend: {
                            display: chartType !== 'doughnut'
                        }
                    },
                    scales: chartType === 'bar' ? {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                precision: 0
                            }
                        }
                    } : {}
                }
            });
            
            // Store chart reference based on chart type
            if (canvasId === 'statusChart') statusChart = chart;
            else if (canvasId === 'priorityChart') priorityChart = chart;
            else if (canvasId === 'categoryChart') categoryChart = chart;
        }
        
        function displayRecentTasks(tasks) {
            const container = document.getElementById('recentTasksList');
            container.innerHTML = '';
            
            if (tasks.length === 0) {
                container.innerHTML = '<p>No recent tasks found.</p>';
                return;
            }
            
            const list = document.createElement('div');
            list.style.display = 'grid';
            list.style.gridTemplateColumns = 'repeat(auto-fill, minmax(300px, 1fr))';
            list.style.gap = '10px';
            
            tasks.forEach(task => {
                const taskEl = document.createElement('div');
                taskEl.style.borderBottom = '1px solid #eee';
                taskEl.style.padding = '10px 0';
                taskEl.style.marginBottom = '10px';
                
                taskEl.innerHTML = `
                    <div style="font-weight: bold;">${task.title}</div>
                    <div style="font-size: 0.9em; color: #666;">
                        ID: ${task.id} | Status: ${task.status} | Priority: ${task.priority} | Category: ${task.category}
                    </div>
                    <div style="font-size: 0.8em; color: #888;">
                        Created: ${task.created_date} | Updated: ${task.updated_date}
                    </div>
                `;
                
                list.appendChild(taskEl);
            });
            
            container.appendChild(list);
        }
        
        async function generateIndexedDBSchema() {
            try {
                const response = await fetch('/api/db/schema');
                if (!response.ok) {
                    throw new Error(`API error: ${response.status} ${response.statusText}`);
                }
                const schema = await response.json();
                
                // Generate IndexedDB setup code
                const indexedDBCodeResponse = await fetch('/api/db/generate-indexeddb');
                if (!indexedDBCodeResponse.ok) {
                    throw new Error(`API error: ${indexedDBCodeResponse.status} ${indexedDBCodeResponse.statusText}`);
                }
                const indexedDBSetupCode = await indexedDBCodeResponse.text();
                
                document.getElementById('indexedDBCode').textContent = indexedDBSetupCode;
                document.getElementById('indexedDBSection').style.display = 'block';
                
                // Scroll to the IndexedDB section
                document.getElementById('indexedDBSection').scrollIntoView({ behavior: 'smooth' });
            } catch (error) {
                console.error('Error generating IndexedDB schema:', error);
                showError('Error generating IndexedDB schema: ' + error.message);
            }
        }
    </script>
</body>
</html>
"""


def index_handler(request):
    """Vercel-compatible handler for the demo dashboard."""
    if request.method == 'GET':
        if request.path == '/' or request.path == '/demo':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'text/html; charset=utf-8'
                },
                'body': generate_dashboard_html()
            }
        elif request.path == '/api/demo/projects':
            projects = generate_demo_projects()
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps(projects)
            }
        elif request.path.startswith('/api/demo/project/'):
            project_name = request.path.split('/')[-1]
            project_details = generate_demo_project_details(project_name)
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps(project_details)
            }
        elif request.path == '/api/db/schema':
            schema = generate_postgresql_schema()
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps(schema)
            }
        elif request.path == '/api/db/generate-indexeddb':
            schema = generate_postgresql_schema()
            indexeddb_code = generate_indexeddb_setup_code(schema)
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'text/plain'
                },
                'body': indexeddb_code
            }
        else:
            return {
                'statusCode': 404,
                'body': 'Not Found'
            }
    else:
        return {
            'statusCode': 405,
            'body': 'Method Not Allowed'
        }


# For local testing with Flask
app = None
def create_app():
    global app
    if app is None:
        app = Flask(__name__)
        
        @app.route('/')
        @app.route('/demo')
        def index():
            return generate_dashboard_html()
        
        @app.route('/api/demo/projects')
        def get_demo_projects():
            projects = generate_demo_projects()
            return jsonify(projects)
        
        @app.route('/api/demo/project/<project_name>')
        def get_demo_project_details(project_name):
            project_details = generate_demo_project_details(project_name)
            return jsonify(project_details)
        
        @app.route('/api/db/schema')
        def get_db_schema():
            schema = generate_postgresql_schema()
            return jsonify(schema)
        
        @app.route('/api/db/generate-indexeddb')
        def get_indexeddb_setup():
            schema = generate_postgresql_schema()
            indexeddb_code = generate_indexeddb_setup_code(schema)
            return indexeddb_code
    
    return app


# This is the function Vercel will call
handler = index_handler


if __name__ == '__main__':
    # For local development
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)