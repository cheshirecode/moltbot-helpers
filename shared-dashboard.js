/**
 * Shared Dashboard Component
 * 
 * A reusable dashboard component that can be used for both main and demo dashboards
 * with feature flags to distinguish between them.
 */

class OpenClawDashboard {
    constructor(options = {}) {
        this.isDemoMode = options.isDemoMode || false;
        this.apiBaseUrl = options.apiBaseUrl || (this.isDemoMode ? '/api/demo' : '/api');
        this.title = options.title || (this.isDemoMode ? 'OpenClaw Demo Dashboard' : 'OpenClaw Task Management Dashboard');
        this.subtitle = options.subtitle || (this.isDemoMode ? 'Showcasing task management capabilities' : 'Visualizing tasks by project from PostgreSQL database');
        this.showDisclaimer = options.showDisclaimer || false;
        this.demoDisclaimer = options.demoDisclaimer || 'This is a demonstration system using synthetic data. The actual OpenClaw system operates independently with real data.';
        
        // Feature flags
        this.features = {
            refreshButton: !this.isDemoMode, // Hide refresh button in demo mode
            loadingIndicator: true,
            errorHandling: true,
            projectSelection: true,
            allProjectsView: true,
            interactiveTasks: options.features?.interactiveTasks ?? false, // New feature flag for interactive task management
            taskEditing: options.features?.taskEditing ?? false,           // Feature flag for task editing
            taskCreation: options.features?.taskCreation ?? false,         // Feature flag for task creation
            dragAndDrop: options.features?.dragAndDrop ?? false,           // Feature flag for drag-and-drop functionality
            timeTracking: options.features?.timeTracking ?? false,         // Feature flag for time tracking
            timelineView: options.features?.timelineView ?? false,         // Feature flag for timeline/Gantt view
            assignmentTracking: options.features?.assignmentTracking ?? false, // Feature flag for assignment tracking
            tagsLabeling: options.features?.tagsLabeling ?? false,          // Feature flag for tags/labeling system
            dependencyTracking: options.features?.dependencyTracking ?? false, // Feature flag for dependency tracking
            taskBreakdowns: options.features?.taskBreakdowns ?? false,        // Feature flag for task breakdowns/subtasks
            burndownChart: options.features?.burndownChart ?? false,         // Feature flag for burn-down charts
            activityHeatMap: options.features?.activityHeatMap ?? false      // Feature flag for activity heat maps
        };
        
        // Merge with any provided feature overrides
        if (options.features) {
            this.features = { ...this.features, ...options.features };
        }
    }

    /**
     * Initialize the dashboard
     */
    async initialize() {
        this.updateUI();
        await this.loadInitialData();
    }

    /**
     * Update the UI based on current configuration
     */
    updateUI() {
        // Update title and subtitle
        document.querySelector('h1').textContent = this.title;
        document.querySelector('.subtitle').textContent = this.subtitle;

        // Show/hide disclaimer if needed
        if (this.showDisclaimer) {
            const disclaimerContainer = document.querySelector('.disclaimer');
            if (disclaimerContainer) {
                disclaimerContainer.innerHTML = `
                    <strong>Note:</strong> ${this.demoDisclaimer}
                `;
                disclaimerContainer.style.display = 'block';
            }
        }

        // Show/hide refresh button based on feature flag
        const refreshButton = document.querySelector('button[onclick="refreshData()"]');
        if (refreshButton) {
            refreshButton.style.display = this.features.refreshButton ? 'inline-block' : 'none';
        }
    }

    /**
     * Load initial data based on dashboard mode
     */
    async loadInitialData() {
        try {
            if (this.features.allProjectsView) {
                await this.loadAllProjects();
            }
        } catch (error) {
            if (this.features.errorHandling) {
                this.showError(`Error initializing dashboard: ${error.message}`);
            }
        }
    }

    /**
     * Load project data by name
     */
    async loadProjectData() {
        const selectedProject = document.getElementById('projectSelect').value;

        if (!selectedProject) {
            if (this.features.errorHandling) {
                this.showError('Please select a project first');
            }
            return;
        }

        if (this.features.loadingIndicator) {
            this.showLoading(true);
            this.hideError();
        }

        try {
            const projectData = await this.fetchProjectData(selectedProject);
            this.displayProjectData(projectData);

            document.getElementById('dashboardContent').style.display = 'block';
            document.getElementById('allProjectsView').style.display = 'none';
        } catch (error) {
            if (this.features.errorHandling) {
                this.showError(`Error loading project data: ${error.message}`);
            }
        } finally {
            if (this.features.loadingIndicator) {
                this.showLoading(false);
            }
        }
    }

    /**
     * Load all projects
     */
    async loadAllProjects() {
        if (this.features.loadingIndicator) {
            this.showLoading(true);
            this.hideError();
        }

        try {
            const allProjectsData = await this.fetchAllProjectsData();
            this.populateProjectSelector(allProjectsData.map(p => p.project));
            this.displayAllProjects(allProjectsData);

            document.getElementById('allProjectsView').style.display = 'block';
            document.getElementById('dashboardContent').style.display = 'none';
        } catch (error) {
            if (this.features.errorHandling) {
                this.showError(`Error loading all projects: ${error.message}`);
            }
        } finally {
            if (this.features.loadingIndicator) {
                this.showLoading(false);
            }
        }
    }

    /**
     * Refresh current view
     */
    async refreshData() {
        // Simply reload the current view
        if (document.getElementById('dashboardContent').style.display === 'block') {
            await this.loadProjectData();
        } else {
            await this.loadAllProjects();
        }
    }

    /**
     * Fetch project data from API
     */
    async fetchProjectData(projectName) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/project/${encodeURIComponent(projectName)}`);
            if (!response.ok) {
                throw new Error(`API error: ${response.status} ${response.statusText}`);
            }
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching project data:', error);
            throw error;
        }
    }

    /**
     * Fetch all projects data from API
     */
    async fetchAllProjectsData() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/projects`);
            if (!response.ok) {
                throw new Error(`API error: ${response.status} ${response.statusText}`);
            }
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching all projects data:', error);
            throw error;
        }
    }

    /**
     * Populate project selector dropdown
     */
    populateProjectSelector(projects) {
        const select = document.getElementById('projectSelect');
        select.innerHTML = `<option value="">${this.isDemoMode ? 'Select a demo project...' : 'Select a project...'}</option>`;

        projects.forEach(project => {
            const option = document.createElement('option');
            option.value = project;
            option.textContent = project;
            select.appendChild(option);
        });
    }

    /**
     * Show loading indicator
     */
    showLoading(show) {
        const loadingIndicator = document.getElementById('loadingIndicator');
        if (loadingIndicator) {
            loadingIndicator.style.display = show ? 'block' : 'none';
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        const errorDiv = document.getElementById('errorMessage');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';

            setTimeout(() => {
                errorDiv.style.display = 'none';
            }, 5000);
        }
    }

    /**
     * Hide error message
     */
    hideError() {
        const errorDiv = document.getElementById('errorMessage');
        if (errorDiv) {
            errorDiv.style.display = 'none';
        }
    }

    /**
     * Display project data
     */
    displayProjectData(data) {
        // Handle both camelCase (for backward compatibility) and snake_case (current API format)
        const totalTasks = data.totalTasks || data.total_tasks || 0;
        const statusCounts = data.statusCounts || data.status_counts || {};
        const priorityCounts = data.priorityCounts || data.priority_counts || {};
        const categoryCounts = data.categoryCounts || data.category_counts || {};
        const recentTasks = data.recentTasks || data.recent_tasks || [];

        // Update stats
        this.updateStats([
            { label: 'Total Tasks', value: totalTasks },
            { label: 'Status Types', value: Object.keys(statusCounts).length },
            { label: 'Priority Levels', value: Object.keys(priorityCounts).length },
            { label: 'Categories', value: Object.keys(categoryCounts).length }
        ]);

        // Create/update charts
        this.createOrUpdateChart('statusChart', 'bar', 'Tasks by Status', statusCounts);
        this.createOrUpdateChart('priorityChart', 'doughnut', 'Tasks by Priority', priorityCounts);
        this.createOrUpdateChart('categoryChart', 'bar', 'Tasks by Category', categoryCounts);

        // Display recent tasks
        this.displayRecentTasks(recentTasks);
        
        // Display timeline view if enabled
        if (this.features.timelineView) {
            this.displayTimelineView(recentTasks);
        }
        
        // Display burn-down chart if enabled
        if (this.features.burndownChart) {
            this.displayBurndownChart(recentTasks);
        }
        
        // Display activity heat map if enabled
        if (this.features.activityHeatMap) {
            this.displayActivityHeatMap(recentTasks);
        }
    }

    /**
     * Display activity heat map showing task activity by day of week
     */
    displayActivityHeatMap(tasks) {
        const container = document.getElementById('activityHeatMap');
        if (!container) return;
        
        // Generate activity data by day of week
        const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        const activityData = days.map(() => Math.floor(Math.random() * 10));
        
        // Normalize for color intensity
        const maxActivity = Math.max(...activityData, 1);
        
        const heatMapHtml = `
            <div style="display: flex; gap: 5px; justify-content: center; align-items: flex-end; height: 150px; padding: 20px;">
                ${days.map((day, i) => {
                    const intensity = activityData[i] / maxActivity;
                    const color = `rgba(67, 97, 238, ${0.2 + intensity * 0.8})`;
                    const height = 20 + (intensity * 100);
                    return `
                        <div style="display: flex; flex-direction: column; align-items: center; gap: 5px;">
                            <div style="width: 40px; height: ${height}px; background: ${color}; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: white; font-size: 0.8em; font-weight: bold;">
                                ${activityData[i]}
                            </div>
                            <span style="font-size: 0.75em; color: #666;">${day}</span>
                        </div>
                    `;
                }).join('')}
            </div>
            <div style="text-align: center; font-size: 0.8em; color: #6c757d; margin-top: 10px;">
                Task Activity by Day of Week
            </div>
        `;
        
        container.innerHTML = heatMapHtml;
    }

    /**
     * Display burn-down chart showing task completion over time
     */
    displayBurndownChart(tasks) {
        const canvas = document.getElementById('burndownChart');
        if (!canvas) return;
        
        // Generate simulated sprint data (in a real system, this would come from actual sprint data)
        const totalTasks = tasks.length;
        const completedTasks = tasks.filter(t => (t.status || t.task_status) === 'completed').length;
        
        // Create 7-day sprint simulation
        const days = ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'];
        const idealBurndown = days.map((_, i) => Math.round(totalTasks * (1 - (i / 6))));
        const actualBurndown = days.map((_, i) => {
            // Simulate actual progress (slightly behind ideal)
            const ideal = totalTasks * (1 - (i / 6));
            return Math.round(Math.max(0, ideal + (Math.random() * 3 - 1)));
        });
        actualBurndown[6] = totalTasks - completedTasks; // Set final day to actual remaining
        
        // Destroy existing chart if it exists
        const existingChart = Chart.getChart('burndownChart');
        if (existingChart) {
            existingChart.destroy();
        }
        
        new Chart(canvas, {
            type: 'line',
            data: {
                labels: days,
                datasets: [
                    {
                        label: 'Ideal Burndown',
                        data: idealBurndown,
                        borderColor: '#6c757d',
                        borderDash: [5, 5],
                        fill: false,
                        tension: 0.1
                    },
                    {
                        label: 'Actual Remaining',
                        data: actualBurndown,
                        borderColor: '#4361ee',
                        backgroundColor: 'rgba(67, 97, 238, 0.1)',
                        fill: true,
                        tension: 0.3
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Sprint Burn-down'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Remaining Tasks'
                        }
                    }
                }
            }
        });
    }

    /**
     * Display timeline/Gantt view of tasks
     */
    displayTimelineView(tasks) {
        const container = document.getElementById('timelineChart');
        if (!container) return;
        
        container.innerHTML = '';
        
        if (tasks.length === 0) {
            container.innerHTML = '<p>No tasks to display in timeline.</p>';
            return;
        }

        // Create a simple timeline visualization
        const timelineHtml = tasks.map((task, index) => {
            const taskId = task.id || task.taskId || task.task_id || '';
            const taskStatus = task.status || task.task_status || 'todo';
            const taskPriority = task.priority || task.task_priority || 'medium';
            const createdDate = task.createdDate || task.created_date || '';
            
            // Calculate bar width based on status
            const progressPercent = taskStatus === 'completed' ? 100 : 
                                    taskStatus === 'in-progress' ? 50 : 
                                    taskStatus === 'review' ? 75 : 10;
            
            // Color based on priority
            const barColor = taskPriority === 'critical' ? '#dc3545' : 
                            taskPriority === 'high' ? '#fd7e14' : 
                            taskPriority === 'medium' ? '#4361ee' : 
                            '#6c757d';
            
            return `
                <div style="display: flex; align-items: center; margin-bottom: 8px; gap: 10px;">
                    <div style="width: 200px; font-size: 0.85em; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${task.title}">
                        #${taskId}: ${task.title}
                    </div>
                    <div style="flex: 1; background: #e9ecef; border-radius: 4px; height: 24px; position: relative;">
                        <div style="width: ${progressPercent}%; background: ${barColor}; height: 100%; border-radius: 4px; transition: width 0.3s;"></div>
                        <span style="position: absolute; right: 5px; top: 3px; font-size: 0.75em; color: #333;">${taskStatus}</span>
                    </div>
                    <div style="width: 80px; font-size: 0.75em; color: #666;">${createdDate}</div>
                </div>
            `;
        }).join('');
        
        container.innerHTML = `
            <div style="padding: 10px;">
                <div style="display: flex; margin-bottom: 15px; gap: 15px; font-size: 0.8em;">
                    <span><span style="display: inline-block; width: 12px; height: 12px; background: #dc3545; border-radius: 2px;"></span> Critical</span>
                    <span><span style="display: inline-block; width: 12px; height: 12px; background: #fd7e14; border-radius: 2px;"></span> High</span>
                    <span><span style="display: inline-block; width: 12px; height: 12px; background: #4361ee; border-radius: 2px;"></span> Medium</span>
                    <span><span style="display: inline-block; width: 12px; height: 12px; background: #6c757d; border-radius: 2px;"></span> Low</span>
                </div>
                ${timelineHtml}
            </div>
        `;
    }

    /**
     * Display all projects
     */
    displayAllProjects(projectsData) {
        const container = document.getElementById('projectListView');
        container.innerHTML = '';

        projectsData.forEach(project => {
            // Handle both camelCase (for backward compatibility) and snake_case (current API format)
            const total = project.total || project.total_tasks || 0;
            const completed = project.completed || project.completed_tasks || 0;
            const inProgress = project.inProgress || project.in_progress_tasks || 0;
            const todo = project.todo || project.todo_tasks || 0;

            const progressPercent = total > 0 ? Math.round((completed / total) * 100) : 0;

            const projectCard = document.createElement('div');
            projectCard.className = 'project-card';
            projectCard.innerHTML = `
                <div class="project-header">
                    <div class="project-name">${project.project}</div>
                    <div class="task-count">${total}</div>
                </div>
                <div>Total Tasks: ${total}</div>
                <div>Completed: ${completed}</div>
                <div>In Progress: ${inProgress}</div>
                <div>To Do: ${todo}</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${progressPercent}%"></div>
                </div>
                <div>${progressPercent}% Complete</div>
            `;

            container.appendChild(projectCard);
        });
    }

    /**
     * Update stats display
     */
    updateStats(stats) {
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

    /**
     * Create or update chart
     */
    createOrUpdateChart(canvasId, chartType, title, dataObj) {
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
        if (canvasId === 'statusChart') window.statusChart = chart;
        else if (canvasId === 'priorityChart') window.statusChart = chart;
        else if (canvasId === 'categoryChart') window.categoryChart = chart;
    }

    /**
     * Display recent tasks in status columns for drag-and-drop
     */
    displayRecentTasks(tasks) {
        // Clear all task columns
        const statusColumns = ['todo', 'in-progress', 'completed', 'blocked', 'review'];
        statusColumns.forEach(status => {
            const column = document.getElementById(`${status.replace('-', '')}Tasks`);
            if (column) {
                column.innerHTML = '';
            }
        });

        if (tasks.length === 0) {
            document.getElementById('todoTasks').innerHTML = '<p>No tasks found.</p>';
            return;
        }

        tasks.forEach(task => {
            // Handle both camelCase (for backward compatibility) and snake_case (current API format)
            const createdDate = task.createdDate || task.created_date || task.created_date_formatted || '';
            const taskId = task.id || task.taskId || task.task_id || '';
            const taskStatus = task.status || task.task_status || 'todo';
            const taskPriority = task.priority || task.task_priority || 'medium';
            const taskCategory = task.category || task.task_category || 'general';
            const taskProject = task.project || '';

            const taskEl = document.createElement('div');
            taskEl.style.borderBottom = '1px solid #eee';
            taskEl.style.padding = '10px 0';
            taskEl.style.marginBottom = '10px';
            taskEl.className = 'task-item';
            taskEl.dataset.taskId = taskId;
            taskEl.dataset.project = taskProject;
            taskEl.draggable = this.features.dragAndDrop;
            taskEl.style.cursor = this.features.dragAndDrop ? 'grab' : 'default';

            // Create the task display with interactive elements if the feature is enabled
            if (this.features.interactiveTasks) {
                taskEl.innerHTML = `
                    <div style="font-weight: bold; display: flex; justify-content: space-between; align-items: center;">
                        <span>${task.title}</span>
                        <span class="priority-badge priority-${taskPriority}" style="background-color: ${
                            taskPriority === 'critical' ? '#dc3545' : 
                            taskPriority === 'high' ? '#fd7e14' : 
                            taskPriority === 'medium' ? '#ffc107' : 
                            '#6c757d'
                        }; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em;">${taskPriority}</span>
                    </div>
                    <div style="font-size: 0.9em; color: #666; display: flex; justify-content: space-between;">
                        <span>ID: ${taskId} | Category: ${taskCategory}</span>
                        <span>Date: ${createdDate}</span>
                    </div>
                    ${this.features.tagsLabeling && task.tags && task.tags.length > 0 ? `
                    <div style="margin-top: 5px; display: flex; flex-wrap: wrap; gap: 4px;">
                        ${task.tags.map(tag => `<span style="background: #e9ecef; color: #495057; padding: 1px 6px; border-radius: 10px; font-size: 0.75em;">#${tag}</span>`).join('')}
                    </div>
                    ` : ''}
                    ${this.features.dependencyTracking ? `
                    <div style="margin-top: 5px; font-size: 0.8em; color: #6c757d;">
                        <span title="Dependencies">🔗 Deps: <span class="task-deps" data-task-id="${taskId}">${task.dependencies || 'None'}</span></span>
                        ${task.blockedBy ? `<span style="color: #dc3545; margin-left: 10px;">⚠️ Blocked by: ${task.blockedBy}</span>` : ''}
                    </div>
                    ` : ''}
                    ${this.features.taskBreakdowns && task.subtasks && task.subtasks.length > 0 ? `
                    <div style="margin-top: 8px; padding-left: 15px; border-left: 2px solid #e9ecef;">
                        <div style="font-size: 0.8em; color: #495057; margin-bottom: 4px;">📋 Subtasks (${task.subtasks.filter(s => s.completed).length}/${task.subtasks.length}):</div>
                        ${task.subtasks.slice(0, 3).map(st => `
                            <div style="font-size: 0.75em; color: #6c757d; padding: 2px 0;">
                                ${st.completed ? '✅' : '⬜'} ${st.title}
                            </div>
                        `).join('')}
                        ${task.subtasks.length > 3 ? `<div style="font-size: 0.7em; color: #adb5bd;">+${task.subtasks.length - 3} more...</div>` : ''}
                    </div>
                    ` : ''}
                    <div style="margin-top: 8px; display: flex; align-items: center; gap: 10px;">
                        <label for="status-select-${taskId}" style="font-size: 0.8em; color: #555;">Status:</label>
                        <select id="status-select-${taskId}" class="status-select" style="padding: 2px 5px; border-radius: 3px; border: 1px solid #ccc;" data-task-id="${taskId}">
                            <option value="todo" ${taskStatus === 'todo' ? 'selected' : ''}>To Do</option>
                            <option value="in-progress" ${taskStatus === 'in-progress' ? 'selected' : ''}>In Progress</option>
                            <option value="completed" ${taskStatus === 'completed' ? 'selected' : ''}>Completed</option>
                            <option value="blocked" ${taskStatus === 'blocked' ? 'selected' : ''}>Blocked</option>
                            <option value="review" ${taskStatus === 'review' ? 'selected' : ''}>Review</option>
                        </select>
                        <button class="update-status-btn" style="padding: 2px 8px; background-color: #007bff; color: white; border: none; border-radius: 3px; font-size: 0.8em;" data-task-id="${taskId}" data-project="${taskProject}">Update</button>
                        ${this.features.taskEditing ? `<button class="edit-task-btn" style="padding: 2px 8px; background-color: #28a745; color: white; border: none; border-radius: 3px; font-size: 0.8em; margin-left: 5px;" data-task-id="${taskId}" data-project="${taskProject}">Edit</button>` : ''}
                    </div>
                    ${this.features.assignmentTracking ? `
                    <div style="margin-top: 8px; display: flex; align-items: center; gap: 10px;">
                        <label for="assignee-${taskId}" style="font-size: 0.8em; color: #555;">Assignee:</label>
                        <select id="assignee-${taskId}" class="assignee-select" style="padding: 2px 5px; border-radius: 3px; border: 1px solid #ccc; flex: 1;" data-task-id="${taskId}">
                            <option value="">Unassigned</option>
                            <option value="user1">User 1</option>
                            <option value="user2">User 2</option>
                            <option value="user3">User 3</option>
                            <option value="team">Team</option>
                        </select>
                        <button class="assign-btn" style="padding: 2px 8px; background-color: #17a2b8; color: white; border: none; border-radius: 3px; font-size: 0.8em;" data-task-id="${taskId}" data-project="${taskProject}">Assign</button>
                    </div>
                    ` : ''}
                    ${this.features.timeTracking ? `
                    <div style="margin-top: 8px; display: flex; align-items: center; gap: 10px;">
                        <label for="time-input-${taskId}" style="font-size: 0.8em; color: #555;">Time:</label>
                        <input type="number" id="time-input-${taskId}" class="time-input" style="width: 60px; padding: 2px 5px; border-radius: 3px; border: 1px solid #ccc;" data-task-id="${taskId}" placeholder="hrs" min="0" step="0.25"/>
                        <button class="log-time-btn" style="padding: 2px 8px; background-color: #28a745; color: white; border: none; border-radius: 3px; font-size: 0.8em;" data-task-id="${taskId}" data-project="${taskProject}">Log Time</button>
                        <span class="logged-time" id="logged-time-${taskId}" style="font-size: 0.8em; color: #6c757d;">0h logged</span>
                    </div>
                    ` : ''}
                `;
            } else {
                // Standard display without interactive elements
                taskEl.innerHTML = `
                    <div style="font-weight: bold;">${task.title}</div>
                    <div style="font-size: 0.9em; color: #666;">
                        ID: ${taskId} | Status: ${taskStatus} | Priority: ${taskPriority} | Category: ${taskCategory} | Date: ${createdDate}
                    </div>
                `;
            }

            // Add drag event listeners if drag-and-drop is enabled
            if (this.features.dragAndDrop) {
                taskEl.addEventListener('dragstart', (e) => {
                    e.dataTransfer.setData('text/plain', JSON.stringify({
                        taskId: taskId,
                        project: taskProject,
                        originalStatus: taskStatus
                    }));
                    taskEl.classList.add('dragging');
                    setTimeout(() => taskEl.style.opacity = '0.5', 0);
                });

                taskEl.addEventListener('dragend', () => {
                    taskEl.classList.remove('dragging');
                    taskEl.style.opacity = '1';
                });
            }

            // Add the task to the appropriate column based on its status
            const columnId = `${taskStatus.replace('-', '')}Tasks`;
            const column = document.getElementById(columnId);
            if (column) {
                column.appendChild(taskEl);
            }
        });

        // Set up drag-and-drop event listeners on the columns if enabled
        if (this.features.dragAndDrop) {
            this.setupDragAndDropEvents();
        }
        
        // Set up event listeners for interactive features if enabled
        if (this.features.interactiveTasks) {
            this.setupInteractiveTaskEvents();
        }
    }

    /**
     * Set up drag-and-drop events for task status columns
     */
    setupDragAndDropEvents() {
        const statusColumns = ['todo', 'in-progress', 'completed', 'blocked', 'review'];
        
        statusColumns.forEach(status => {
            const columnId = `${status.replace('-', '')}Tasks`;
            const column = document.getElementById(columnId);
            
            if (column) {
                column.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    column.style.borderColor = '#4361ee';
                    column.style.backgroundColor = '#f0f5ff';
                });

                column.addEventListener('dragleave', (e) => {
                    e.preventDefault();
                    column.style.borderColor = '#dee2e6';
                    column.style.backgroundColor = 'transparent';
                });

                column.addEventListener('drop', (e) => {
                    e.preventDefault();
                    column.style.borderColor = '#dee2e6';
                    column.style.backgroundColor = 'transparent';

                    const data = JSON.parse(e.dataTransfer.getData('text/plain'));
                    const draggedTaskId = data.taskId;
                    const draggedProject = data.project;
                    const newStatus = status; // The status of the column where it was dropped
                    
                    // Update the task status via API
                    this.updateTaskStatus(draggedTaskId, draggedProject, newStatus);
                });
            }
        });
    }

    /**
     * Set up event listeners for interactive task features
     */
    setupInteractiveTaskEvents() {
        // Add event listener for update status buttons using event delegation
        const recentTasksList = document.getElementById('recentTasksList');
        if (recentTasksList) {
            recentTasksList.addEventListener('click', (event) => {
                if (event.target.classList.contains('update-status-btn')) {
                    event.preventDefault();
                    const taskId = event.target.getAttribute('data-task-id');
                    const project = event.target.getAttribute('data-project');
                    if (taskId && project) {
                        this.updateTaskStatus(taskId, project);
                    }
                }

                // Add event listener for edit task buttons using event delegation
                if (event.target.classList.contains('edit-task-btn')) {
                    event.preventDefault();
                    const taskId = event.target.getAttribute('data-task-id');
                    const project = event.target.getAttribute('data-project');
                    if (taskId && project) {
                        this.openEditTaskModal(taskId, project);
                    }
                }

                // Add event listener for log time buttons using event delegation
                if (this.features.timeTracking && event.target.classList.contains('log-time-btn')) {
                    event.preventDefault();
                    const taskId = event.target.getAttribute('data-task-id');
                    const project = event.target.getAttribute('data-project');
                    if (taskId && project) {
                        this.logTimeForTask(taskId, project);
                    }
                }
            });
        }
    }

    /**
     * Open a modal for creating a new task
     */
    openCreateTaskModal() {
        if (!this.features.taskCreation) {
            console.log('Task creation feature is disabled');
            this.showError('Task creation is disabled in this mode.');
            return;
        }

        const projectSelect = document.getElementById('projectSelect');
        const selectedProject = projectSelect ? projectSelect.value : '';

        const modalHtml = `
            <div id="createTaskModal" style="
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center;
                z-index: 1000;
            ">
                <div style="
                    background: white; padding: 20px; border-radius: 8px; width: 400px;
                    max-width: 90%; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                ">
                    <h3 style="margin-top: 0;">Create New Task</h3>
                    <form id="createTaskForm">
                        <div style="margin-bottom: 10px;">
                            <label for="createTaskProject">Project:</label>
                            <input type="text" id="createTaskProject" value="${selectedProject}" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;" required />
                        </div>
                        <div style="margin-bottom: 10px;">
                            <label for="createTaskTitle">Title:</label>
                            <input type="text" id="createTaskTitle" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;" required />
                        </div>
                        <div style="margin-bottom: 10px;">
                            <label for="createTaskDescription">Description:</label>
                            <textarea id="createTaskDescription" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;"></textarea>
                        </div>
                        <div style="margin-bottom: 10px;">
                            <label for="createTaskStatus">Status:</label>
                            <select id="createTaskStatus" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
                                <option value="todo">To Do</option>
                                <option value="in-progress">In Progress</option>
                                <option value="completed">Completed</option>
                                <option value="blocked">Blocked</option>
                                <option value="review">Review</option>
                            </select>
                        </div>
                        <div style="margin-bottom: 10px;">
                            <label for="createTaskPriority">Priority:</label>
                            <select id="createTaskPriority" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
                                <option value="critical">Critical</option>
                                <option value="high">High</option>
                                <option value="medium" selected>Medium</option>
                                <option value="low">Low</option>
                            </select>
                        </div>
                        <div style="margin-bottom: 10px;">
                            <label for="createTaskCategory">Category:</label>
                            <input type="text" id="createTaskCategory" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;" value="general" required />
                        </div>
                        <div style="text-align: right; margin-top: 20px;">
                            <button type="button" id="cancelCreateTask" style="background-color: #6c757d; margin-right: 10px;">Cancel</button>
                            <button type="submit" style="background-color: #28a745;">Create Task</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);

        // Add event listeners for modal buttons
        document.getElementById('cancelCreateTask').addEventListener('click', () => {
            document.getElementById('createTaskModal').remove();
        });

        document.getElementById('createTaskForm').addEventListener('submit', (event) => {
            event.preventDefault();
            this.createNewTask();
        });
    }

    /**
     * Create new task via API
     */
    async createNewTask() {
        if (!this.features.taskCreation) {
            console.log('Task creation feature is disabled');
            return;
        }

        if (this.features.loadingIndicator) {
            this.showLoading(true);
        }

        try {
            const newTaskData = {
                project: document.getElementById('createTaskProject').value,
                title: document.getElementById('createTaskTitle').value,
                description: document.getElementById('createTaskDescription').value,
                status: document.getElementById('createTaskStatus').value,
                priority: document.getElementById('createTaskPriority').value,
                category: document.getElementById('createTaskCategory').value,
                created_date: new Date().toISOString().split('T')[0],
                updated_date: new Date().toISOString().split('T')[0]
            };

            const response = await fetch(`${this.apiBaseUrl}/project/${encodeURIComponent(newTaskData.project)}/task`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(newTaskData)
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.status} ${response.statusText}`);
            }

            document.getElementById('createTaskModal').remove();
            this.showMessage(`Task '${newTaskData.title}' created successfully`, 'success');
            await this.refreshData(); // Refresh to reflect new task

        } catch (error) {
            if (this.features.errorHandling) {
                this.showError(`Error creating new task: ${error.message}`);
            }
        } finally {
            if (this.features.loadingIndicator) {
                this.showLoading(false);
            }
        }
    }


    /**
     * Open a modal for editing task details
     */
    async openEditTaskModal(taskId, project) {
        if (!this.features.taskEditing) {
            console.log('Task editing feature is disabled');
            return;
        }

        if (this.features.loadingIndicator) {
            this.showLoading(true);
        }

        try {
            // Fetch task details for pre-filling the form
            const taskDetails = await this.fetchTaskDetails(taskId, project);
            if (!taskDetails) {
                throw new Error('Task details not found');
            }

            // Create and display the modal
            const modalHtml = `
                <div id="editTaskModal" style="
                    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                    background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center;
                    z-index: 1000;
                ">
                    <div style="
                        background: white; padding: 20px; border-radius: 8px; width: 400px;
                        max-width: 90%; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    ">
                        <h3 style="margin-top: 0;">Edit Task: ${taskDetails.title}</h3>
                        <form id="editTaskForm">
                            <input type="hidden" id="editTaskId" value="${taskDetails.id}" />
                            <input type="hidden" id="editTaskProject" value="${taskDetails.project}" />
                            
                            <div style="margin-bottom: 10px;">
                                <label for="editTaskTitle">Title:</label>
                                <input type="text" id="editTaskTitle" value="${taskDetails.title}" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;" required />
                            </div>
                            <div style="margin-bottom: 10px;">
                                <label for="editTaskDescription">Description:</label>
                                <textarea id="editTaskDescription" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">${taskDetails.description || ''}</textarea>
                            </div>
                            <div style="margin-bottom: 10px;">
                                <label for="editTaskStatus">Status:</label>
                                <select id="editTaskStatus" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
                                    <option value="todo" ${taskDetails.status === 'todo' ? 'selected' : ''}>To Do</option>
                                    <option value="in-progress" ${taskDetails.status === 'in-progress' ? 'selected' : ''}>In Progress</option>
                                    <option value="completed" ${taskDetails.status === 'completed' ? 'selected' : ''}>Completed</option>
                                    <option value="blocked" ${taskDetails.status === 'blocked' ? 'selected' : ''}>Blocked</option>
                                    <option value="review" ${taskDetails.status === 'review' ? 'selected' : ''}>Review</option>
                                </select>
                            </div>
                            <div style="margin-bottom: 10px;">
                                <label for="editTaskPriority">Priority:</label>
                                <select id="editTaskPriority" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
                                    <option value="critical" ${taskDetails.priority === 'critical' ? 'selected' : ''}>Critical</option>
                                    <option value="high" ${taskDetails.priority === 'high' ? 'selected' : ''}>High</option>
                                    <option value="medium" ${taskDetails.priority === 'medium' ? 'selected' : ''}>Medium</option>
                                    <option value="low" ${taskDetails.priority === 'low' ? 'selected' : ''}>Low</option>
                                </select>
                            </div>
                            <div style="text-align: right; margin-top: 20px;">
                                <button type="button" id="cancelEditTask" style="background-color: #6c757d; margin-right: 10px;">Cancel</button>
                                <button type="submit" style="background-color: #28a745;">Save Changes</button>
                            </div>
                        </form>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHtml);

            // Add event listeners for modal buttons
            document.getElementById('cancelEditTask').addEventListener('click', () => {
                document.getElementById('editTaskModal').remove();
            });

            document.getElementById('editTaskForm').addEventListener('submit', (event) => {
                event.preventDefault();
                this.saveTaskChanges();
            });

        } catch (error) {
            if (this.features.errorHandling) {
                this.showError(`Error opening edit modal: ${error.message}`);
            }
        } finally {
            if (this.features.loadingIndicator) {
                this.showLoading(false);
            }
        }
    }

    /**
     * Fetch single task details from API
     */
    async fetchTaskDetails(taskId, project) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/project/${encodeURIComponent(project)}/task/${encodeURIComponent(taskId)}`);
            if (!response.ok) {
                throw new Error(`API error: ${response.status} ${response.statusText}`);
            }
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching task details:', error);
            throw error;
        }
    }

    /**
     * Save task changes from the modal form
     */
    async saveTaskChanges() {
        if (!this.features.taskEditing) {
            console.log('Task editing feature is disabled');
            return;
        }

        if (this.features.loadingIndicator) {
            this.showLoading(true);
        }

        try {
            const taskId = document.getElementById('editTaskId').value;
            const project = document.getElementById('editTaskProject').value;
            const updatedData = {
                title: document.getElementById('editTaskTitle').value,
                description: document.getElementById('editTaskDescription').value,
                status: document.getElementById('editTaskStatus').value,
                priority: document.getElementById('editTaskPriority').value,
                updated_date: new Date().toISOString().split('T')[0]
            };

            const response = await fetch(`${this.apiBaseUrl}/project/${encodeURIComponent(project)}/task/${encodeURIComponent(taskId)}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(updatedData)
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.status} ${response.statusText}`);
            }

            document.getElementById('editTaskModal').remove();
            this.showMessage(`Task ${taskId} updated successfully`, 'success');
            await this.refreshData(); // Refresh to reflect changes

        } catch (error) {
            if (this.features.errorHandling) {
                this.showError(`Error saving task changes: ${error.message}`);
            }
        } finally {
            if (this.features.loadingIndicator) {
                this.showLoading(false);
            }
        }
    }

    /**
     * Update task status via API
     */
    async updateTaskStatus(taskId, project, newStatus = null) {
        if (!this.features.interactiveTasks) {
            console.log('Interactive tasks feature is disabled');
            return;
        }

        if (this.features.loadingIndicator) {
            this.showLoading(true);
        }

        try {
            // If newStatus is not provided, get it from the select element
            if (!newStatus) {
                const statusSelect = document.getElementById(`status-select-${taskId}`);
                if (!statusSelect) {
                    throw new Error(`Status select element not found for task ${taskId}`);
                }
                newStatus = statusSelect.value;
            }

            // Prepare the update data
            const updateData = {
                status: newStatus,
                updated_date: new Date().toISOString().split('T')[0]
            };

            // Make API call to update task status
            const response = await fetch(`${this.apiBaseUrl}/project/${encodeURIComponent(project)}/task/${encodeURIComponent(taskId)}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(updateData)
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.status} ${response.statusText}`);
            }

            // Show success message
            this.showMessage(`Task ${taskId} status updated to ${newStatus}`, 'success');

            // Refresh the current view to show updated data
            await this.refreshData();

        } catch (error) {
            if (this.features.errorHandling) {
                this.showError(`Error updating task status: ${error.message}`);
            }
        } finally {
            if (this.features.loadingIndicator) {
                this.showLoading(false);
            }
        }
    }

    /**
     * Log time for a specific task
     */
    async logTimeForTask(taskId, project) {
        if (!this.features.timeTracking) {
            console.log('Time tracking feature is disabled');
            return;
        }

        if (this.features.loadingIndicator) {
            this.showLoading(true);
        }

        try {
            // Get the time input value
            const timeInput = document.getElementById(`time-input-${taskId}`);
            if (!timeInput) {
                throw new Error(`Time input element not found for task ${taskId}`);
            }

            const timeValue = parseFloat(timeInput.value);
            if (isNaN(timeValue) || timeValue <= 0) {
                throw new Error('Please enter a valid positive time value');
            }

            // For now, we'll just show a success message since the backend doesn't have time tracking yet
            // In a full implementation, we would make an API call to log the time
            
            // Update the logged time display
            const loggedTimeSpan = document.getElementById(`logged-time-${taskId}`);
            if (loggedTimeSpan) {
                // For now, just show a simple message - in a real implementation we'd track actual logged time
                loggedTimeSpan.textContent = `${timeValue}h logged`;
            }

            this.showMessage(`Logged ${timeValue} hours for task ${taskId}`, 'success');
            
            // Clear the input
            timeInput.value = '';

        } catch (error) {
            if (this.features.errorHandling) {
                this.showError(`Error logging time: ${error.message}`);
            }
        } finally {
            if (this.features.loadingIndicator) {
                this.showLoading(false);
            }
        }
    }

    /**
     * Show temporary message
     */
    showMessage(message, type = 'info') {
        // Create a temporary message div
        const messageDiv = document.createElement('div');
        messageDiv.style.position = 'fixed';
        messageDiv.style.top = '20px';
        messageDiv.style.right = '20px';
        messageDiv.style.padding = '10px 15px';
        messageDiv.style.borderRadius = '4px';
        messageDiv.style.color = 'white';
        messageDiv.style.backgroundColor = type === 'success' ? '#28a745' : '#007bff';
        messageDiv.style.zIndex = '1000';
        messageDiv.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
        messageDiv.textContent = message;

        document.body.appendChild(messageDiv);

        // Remove the message after 3 seconds
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.parentNode.removeChild(messageDiv);
            }
        }, 3000);
    }
}

// Export for use in both main and demo dashboards
if (typeof module !== 'undefined' && module.exports) {
    module.exports = OpenClawDashboard;
}