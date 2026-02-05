/**
 * Universal Data Adapter for Browser Environment
 * Works with both REST API (for PostgreSQL) and IndexedDB
 */

class DataSource {
    constructor() {
        this.type = 'abstract';
    }

    async getProjects() {
        throw new Error('Method getProjects must be implemented');
    }

    async getProjectDetails(projectName) {
        throw new Error('Method getProjectDetails must be implemented');
    }

    async updateProject(projectData) {
        throw new Error('Method updateProject must be implemented');
    }
}

class ApiAdapter extends DataSource {
    constructor(baseUrl = '/api') {
        super();
        this.type = 'api';
        this.baseUrl = baseUrl;
    }

    async getProjects() {
        try {
            const response = await fetch(`${this.baseUrl}/demo/projects`);
            if (!response.ok) {
                throw new Error(`API error: ${response.status} ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching projects from API:', error);
            // Fallback to synthetic data if API fails
            return this.generateSyntheticProjects();
        }
    }

    async getProjectDetails(projectName) {
        try {
            const response = await fetch(`${this.baseUrl}/demo/project/${encodeURIComponent(projectName)}`);
            if (!response.ok) {
                throw new Error(`API error: ${response.status} ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching project details from API:', error);
            // Fallback to synthetic data if API fails
            return this.generateSyntheticProjectDetails(projectName);
        }
    }

    async updateProject(projectData) {
        try {
            const response = await fetch(`${this.baseUrl}/project/${projectData.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(projectData)
            });
            if (!response.ok) {
                throw new Error(`API error: ${response.status} ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error updating project via API:', error);
            throw error;
        }
    }

    // Synthetic data generators for fallback
    generateSyntheticProjects() {
        const projectNames = [
            'openclaw-core', 'moltbot-integration', 'ai-automation', 'data-pipeline',
            'workflow-engine', 'knowledge-base', 'task-orchestration', 'sync-service'
        ];

        const projects = projectNames.map(name => {
            const totalTasks = Math.floor(Math.random() * 135) + 15; // 15-150
            const completedTasks = Math.floor(Math.random() * (totalTasks + 1));
            const inProgressTasks = Math.floor(Math.random() * (totalTasks - completedTasks + 1));
            const todoTasks = totalTasks - completedTasks - inProgressTasks;

            return {
                project: name,
                total_tasks: totalTasks,
                completed_tasks: completedTasks,
                in_progress_tasks: inProgressTasks,
                todo_tasks: todoTasks
            };
        });

        return projects.sort((a, b) => b.total_tasks - a.total_tasks);
    }

    generateSyntheticProjectDetails(projectName) {
        const statuses = ['completed', 'in-progress', 'todo', 'blocked', 'review'];
        const priorities = ['critical', 'high', 'medium', 'low'];
        const categories = ['development', 'testing', 'documentation', 'research', 'maintenance', 'design'];

        const totalTasks = Math.floor(Math.random() * 40) + 10; // 10-50

        // Generate status distribution
        const statusCounts = {};
        let remaining = totalTasks;
        for (let i = 0; i < statuses.length - 1; i++) {
            if (remaining <= 0) break;
            const count = Math.floor(Math.random() * Math.min(remaining, Math.floor(totalTasks * 0.4))) + 1;
            statusCounts[statuses[i]] = count;
            remaining -= count;
        }
        statusCounts[statuses[statuses.length - 1]] = Math.max(0, remaining);

        // Generate priority distribution
        const priorityCounts = {};
        remaining = totalTasks;
        for (let i = 0; i < priorities.length - 1; i++) {
            if (remaining <= 0) break;
            const count = Math.floor(Math.random() * Math.min(remaining, Math.floor(totalTasks * 0.3))) + 1;
            priorityCounts[priorities[i]] = count;
            remaining -= count;
        }
        priorityCounts[priorities[priorities.length - 1]] = Math.max(0, remaining);

        // Generate category distribution
        const categoryCounts = {};
        remaining = totalTasks;
        for (let i = 0; i < categories.length - 1; i++) {
            if (remaining <= 0) break;
            const count = Math.floor(Math.random() * Math.min(remaining, Math.floor(totalTasks * 0.3))) + 1;
            categoryCounts[categories[i]] = count;
            remaining -= count;
        }
        categoryCounts[categories[categories.length - 1]] = Math.max(0, remaining);

        // Generate recent tasks
        const recentTasks = [];
        const numRecentTasks = Math.min(10, totalTasks);
        for (let i = 0; i < numRecentTasks; i++) {
            const daysAgoCreated = Math.floor(Math.random() * 30);
            const daysAgoUpdated = Math.floor(Math.random() * Math.min(14, daysAgoCreated + 1));

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
            statusCounts,
            priorityCounts,
            categoryCounts,
            recentTasks,
            totalTasks
        };
    }
}

class IndexedDBAdapter extends DataSource {
    constructor(dbName = 'openclaw_mirror', version = 1) {
        super();
        this.type = 'indexeddb';
        this.dbName = dbName;
        this.version = version;
        this.db = null;
    }

    async init() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.version);

            request.onerror = () => reject(request.error);
            request.onsuccess = () => {
                this.db = request.result;
                resolve(this.db);
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;

                // Create object stores based on our schema
                if (!db.objectStoreNames.contains('project_tracker')) {
                    const store = db.createObjectStore('project_tracker', { keyPath: 'id', autoIncrement: true });
                    
                    // Create indexes
                    store.createIndex('project', 'project', { unique: false });
                    store.createIndex('status', 'status', { unique: false });
                    store.createIndex('priority', 'priority', { unique: false });
                    store.createIndex('category', 'category', { unique: false });
                    store.createIndex('created_date', 'created_date', { unique: false });
                    store.createIndex('updated_date', 'updated_date', { unique: false });
                }
            };
        });
    }

    async getProjects() {
        if (!this.db) {
            await this.init();
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['project_tracker'], 'readonly');
            const store = transaction.objectStore('project_tracker');
            const index = store.index('project');

            // Group projects by name and count tasks
            const projectsMap = new Map();

            index.openCursor().onsuccess = (event) => {
                const cursor = event.target.result;
                if (cursor) {
                    const project = cursor.key;
                    if (!projectsMap.has(project)) {
                        projectsMap.set(project, {
                            project: project,
                            total_tasks: 0,
                            completed_tasks: 0,
                            in_progress_tasks: 0,
                            todo_tasks: 0
                        });
                    }

                    const projectData = projectsMap.get(project);
                    projectData.total_tasks++;
                    
                    const value = cursor.value;
                    if (value.status === 'completed') {
                        projectData.completed_tasks++;
                    } else if (value.status === 'in-progress') {
                        projectData.in_progress_tasks++;
                    } else if (value.status === 'todo') {
                        projectData.todo_tasks++;
                    }

                    cursor.continue();
                } else {
                    // Convert map to array and sort
                    const projects = Array.from(projectsMap.values()).sort((a, b) => b.total_tasks - a.total_tasks);
                    resolve(projects);
                }
            };

            transaction.onerror = () => reject(transaction.error);
        });
    }

    async getProjectDetails(projectName) {
        if (!this.db) {
            await this.init();
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['project_tracker'], 'readonly');
            const store = transaction.objectStore('project_tracker');

            const index = store.index('project');
            const request = index.getAll(IDBKeyRange.only(projectName));

            request.onsuccess = () => {
                const tasks = request.result;
                
                // Count statuses, priorities, and categories
                const statusCounts = { completed: 0, 'in-progress': 0, todo: 0, blocked: 0, review: 0 };
                const priorityCounts = { critical: 0, high: 0, medium: 0, low: 0 };
                const categoryCounts = { 
                    development: 0, testing: 0, documentation: 0, 
                    research: 0, maintenance: 0, design: 0 
                };

                tasks.forEach(task => {
                    if (statusCounts.hasOwnProperty(task.status)) {
                        statusCounts[task.status]++;
                    }
                    if (priorityCounts.hasOwnProperty(task.priority)) {
                        priorityCounts[task.priority]++;
                    }
                    if (categoryCounts.hasOwnProperty(task.category)) {
                        categoryCounts[task.category]++;
                    }
                });

                resolve({
                    project: projectName,
                    statusCounts,
                    priorityCounts,
                    categoryCounts,
                    recentTasks: tasks.slice(0, 10), // Last 10 tasks
                    totalTasks: tasks.length
                });
            };

            request.onerror = () => reject(request.error);
        });
    }

    async updateProject(projectData) {
        if (!this.db) {
            await this.init();
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['project_tracker'], 'readwrite');
            const store = transaction.objectStore('project_tracker');

            // For updating, we need to handle individual tasks
            // This is a simplified example - in practice you might update multiple records
            const request = store.put(projectData);

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    // Method to sync from API source
    async syncFromApi(apiAdapter) {
        try {
            // Clear existing data
            await this.clearStore('project_tracker');
            
            // Get fresh data from API
            const projects = await apiAdapter.getProjects();
            
            // Get detailed data for each project
            for (const project of projects) {
                const details = await apiAdapter.getProjectDetails(project.project);
                
                // Add each task to IndexedDB
                for (const task of details.recentTasks) {
                    await this.addTask(task);
                }
            }
            
            console.log('Sync from API completed successfully');
            return { success: true, message: 'Sync completed' };
        } catch (error) {
            console.error('Error syncing from API:', error);
            return { success: false, message: error.message };
        }
    }

    async addTask(task) {
        if (!this.db) {
            await this.init();
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['project_tracker'], 'readwrite');
            const store = transaction.objectStore('project_tracker');
            
            // Ensure the task has required fields
            const taskToAdd = { ...task };
            if (!taskToAdd.id) {
                delete taskToAdd.id; // Let IndexedDB auto-generate
            }
            
            const request = store.add(taskToAdd);

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async clearStore(storeName) {
        if (!this.db) {
            await this.init();
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            const request = store.clear();

            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }
}

class UniversalDataAdapter {
    constructor(adapter) {
        this.adapter = adapter;
    }

    async getProjects() {
        return await this.adapter.getProjects();
    }

    async getProjectDetails(projectName) {
        return await this.adapter.getProjectDetails(projectName);
    }

    async updateProject(projectData) {
        return await this.adapter.updateProject(projectData);
    }

    // Method to switch adapters dynamically
    setAdapter(newAdapter) {
        this.adapter = newAdapter;
    }

    // Method to get adapter type
    getType() {
        return this.adapter?.type || 'unknown';
    }
}

// Export for use in modules (if using ES6 modules)
// export { ApiAdapter, IndexedDBAdapter, UniversalDataAdapter };

// For Vercel/Node environment, we'll make it available globally
if (typeof window !== 'undefined') {
    window.ApiAdapter = ApiAdapter;
    window.IndexedDBAdapter = IndexedDBAdapter;
    window.UniversalDataAdapter = UniversalDataAdapter;
}