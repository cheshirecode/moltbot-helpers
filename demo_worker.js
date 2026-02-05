// OpenClaw Demo Cloudflare Worker
//
// A serverless implementation of the OpenClaw demo dashboard
// Generates synthetic data for demonstration purposes

import { Hono } from 'https://deno.land/x/hono/mod.ts';

const app = new Hono();

// Generate synthetic project data for demo
function generateDemoProjects() {
  const projectNames = [
    'openclaw-core', 'moltbot-integration', 'ai-automation', 'data-pipeline',
    'workflow-engine', 'knowledge-base', 'task-orchestration', 'sync-service'
  ];

  const demoProjects = [];
  for (const name of projectNames) {
    const totalTasks = Math.floor(Math.random() * 135) + 15;
    const completedTasks = Math.floor(Math.random() * (totalTasks + 1));
    const inProgressTasks = Math.floor(Math.random() * (totalTasks - completedTasks + 1));
    const todoTasks = totalTasks - completedTasks - inProgressTasks;

    demoProjects.push({
      project: name,
      total_tasks: totalTasks,
      completed_tasks: completedTasks,
      in_progress_tasks: inProgressTasks,
      todo_tasks: todoTasks
    });
  }

  return demoProjects.sort((a, b) => b.total_tasks - a.total_tasks);
}

function generateDemoProjectDetails(projectName) {
  // Possible values for demo data
  const statuses = ['completed', 'in-progress', 'todo', 'blocked', 'review'];
  const priorities = ['critical', 'high', 'medium', 'low'];
  const categories = ['development', 'testing', 'documentation', 'research', 'maintenance', 'design'];

  // Generate random counts
  const totalTasks = Math.floor(Math.random() * 40) + 10;

  // Generate status distribution
  const statusCounts = {};
  let remaining = totalTasks;
  for (let i = 0; i < statuses.length - 1; i++) {
    if (remaining <= 0) break;
    const count = Math.floor(Math.random() * Math.min(remaining, Math.floor(totalTasks * 0.4))) + 1;
    statusCounts[statuses[i]] = count;
    remaining -= count;
  }
  // Assign remaining to last status
  statusCounts[statuses[statuses.length - 1]] = remaining;

  // Generate priority distribution
  const priorityCounts = {};
  remaining = totalTasks;
  for (let i = 0; i < priorities.length - 1; i++) {
    if (remaining <= 0) break;
    const count = Math.floor(Math.random() * Math.min(remaining, Math.floor(totalTasks * 0.3))) + 1;
    priorityCounts[priorities[i]] = count;
    remaining -= count;
  }
  priorityCounts[priorities[priorities.length - 1]] = remaining;

  // Generate category distribution
  const categoryCounts = {};
  remaining = totalTasks;
  for (let i = 0; i < categories.length - 1; i++) {
    if (remaining <= 0) break;
    const count = Math.floor(Math.random() * Math.min(remaining, Math.floor(totalTasks * 0.3))) + 1;
    categoryCounts[categories[i]] = count;
    remaining -= count;
  }
  categoryCounts[categories[categories.length - 1]] = remaining;

  // Generate recent tasks
  const recentTasks = [];
  for (let i = 0; i < Math.min(10, totalTasks); i++) {
    const daysAgoCreated = Math.floor(Math.random() * 31);
    const daysAgoUpdated = Math.floor(Math.random() * 15);
    
    recentTasks.push({
      id: Math.floor(Math.random() * 9000) + 1000,
      title: `Demo task ${i+1} for ${projectName}`,
      status: statuses[Math.floor(Math.random() * statuses.length)],
      priority: priorities[Math.floor(Math.random() * priorities.length)],
      category: categories[Math.floor(Math.random() * categories.length)],
      created_date: new Date(Date.now() - daysAgoCreated * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      updated_date: new Date(Date.now() - daysAgoUpdated * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      tags: ['demo', 'showcase', 'example']
    });
  }

  return {
    project: projectName,
    statusCounts: statusCounts,
    priorityCounts: priorityCounts,
    categoryCounts: categoryCounts,
    recentTasks: recentTasks,
    totalTasks: totalTasks
  };
}

// HTML template for the dashboard
const dashboardHtml = `
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
                const projects = await response.json();
                
                // Populate project selector
                populateProjectSelector(projects.map(p => p.project));
                
                // Display all projects
                displayAllProjects(projects);
                
                document.getElementById('allProjectsView').style.display = 'block';
                document.getElementById('dashboardContent').style.display = 'none';
            } catch (error) {
                console.error('Error loading all projects:', error);
                alert('Error loading projects: ' + error.message);
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
                alert('Please select a project first');
                return;
            }
            
            try {
                // Fetch demo project details
                const response = await fetch('/api/demo/project/' + encodeURIComponent(selectedProject));
                const projectData = await response.json();
                
                displayProjectData(projectData);
                
                document.getElementById('dashboardContent').style.display = 'block';
                document.getElementById('allProjectsView').style.display = 'none';
            } catch (error) {
                console.error('Error loading project data:', error);
                alert('Error loading project data: ' + error.message);
            }
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
                projectCard.innerHTML = \`
                    <div class="project-header">
                        <div class="project-name">\${project.project}</div>
                        <div class="task-count">\${project.total_tasks}</div>
                    </div>
                    <div>Total Tasks: \${project.total_tasks}</div>
                    <div>Completed: \${project.completed_tasks}</div>
                    <div>In Progress: \${project.in_progress_tasks}</div>
                    <div>To Do: \${project.todo_tasks}</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: \${progressPercent}%"></div>
                    </div>
                    <div>\${progressPercent}% Complete</div>
                \`;
                
                container.appendChild(projectCard);
            });
        }
        
        function updateStats(stats) {
            const container = document.getElementById('statsGrid');
            container.innerHTML = '';
            
            stats.forEach(stat => {
                const statCard = document.createElement('div');
                statCard.className = 'stat-card';
                statCard.innerHTML = \`
                    <div class="stat-value">\${stat.value}</div>
                    <div class="stat-label">\${stat.label}</div>
                \`;
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
                
                taskEl.innerHTML = \`
                    <div style="font-weight: bold;">\${task.title}</div>
                    <div style="font-size: 0.9em; color: #666;">
                        ID: \${task.id} | Status: \${task.status} | Priority: \${task.priority} | Category: \${task.category}
                    </div>
                    <div style="font-size: 0.8em; color: #888;">
                        Created: \${task.created_date} | Updated: \${task.updated_date}
                    </div>
                \`;
                
                list.appendChild(taskEl);
            });
            
            container.appendChild(list);
        }
    </script>
</body>
</html>
`;

// Define routes
app.get('/', (c) => {
  return c.html(dashboardHtml);
});

app.get('/demo', (c) => {
  return c.html(dashboardHtml);
});

app.get('/api/demo/projects', (c) => {
  try {
    const projects = generateDemoProjects();
    return c.json(projects);
  } catch (error) {
    return c.json({ error: error.toString() }, 500);
  }
});

app.get('/api/demo/project/:projectName', (c) => {
  try {
    const projectName = c.req.param('projectName');
    const projectDetails = generateDemoProjectDetails(projectName);
    return c.json(projectDetails);
  } catch (error) {
    return c.json({ error: error.toString() }, 500);
  }
});

// Export the handler for Cloudflare Workers
export default {
  fetch: app.fetch,
};