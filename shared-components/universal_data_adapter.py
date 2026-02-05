"""
Universal Data Adapter for OpenClaw Systems
Provides consistent interface for both PostgreSQL and IndexedDB
"""

import json
import random
from datetime import datetime, timedelta
from abc import ABC, abstractmethod


class DataSource(ABC):
    """Abstract base class for data sources."""
    
    @abstractmethod
    def get_projects(self):
        pass
    
    @abstractmethod
    def get_project_details(self, project_name):
        pass
    
    @abstractmethod
    def update_project(self, project_data):
        pass


class PostgreSQLAdapter(DataSource):
    """Adapter for PostgreSQL data source (real data)."""
    
    def __init__(self, connection):
        self.connection = connection
    
    def get_projects(self):
        """Fetch projects from PostgreSQL database."""
        # This would connect to the real PostgreSQL database
        # For demo purposes, returning empty list
        return []
    
    def get_project_details(self, project_name):
        """Fetch project details from PostgreSQL."""
        # This would query the real database
        # For demo purposes, returning empty dict
        return {}
    
    def update_project(self, project_data):
        """Update project in PostgreSQL."""
        # This would update the real database
        pass


class IndexedDBAdapter(DataSource):
    """Adapter for IndexedDB data source (mirrored data)."""
    
    def __init__(self):
        # In a real implementation, this would interact with IndexedDB
        # via JavaScript APIs. This is a Python representation for server-side
        pass
    
    def get_projects(self):
        """Fetch projects from IndexedDB (simulated)."""
        # Return empty list - would fetch from IndexedDB in browser
        return []
    
    def get_project_details(self, project_name):
        """Fetch project details from IndexedDB (simulated)."""
        # Return empty dict - would fetch from IndexedDB in browser
        return {}
    
    def update_project(self, project_data):
        """Update project in IndexedDB (simulated)."""
        # Would update IndexedDB in browser
        pass


class UniversalDataAdapter:
    """Universal adapter that abstracts data source differences."""
    
    def __init__(self, data_source: DataSource):
        self.data_source = data_source
    
    def get_projects(self):
        """Get projects from the underlying data source."""
        return self.data_source.get_projects()
    
    def get_project_details(self, project_name):
        """Get project details from the underlying data source."""
        return self.data_source.get_project_details(project_name)
    
    def update_project(self, project_data):
        """Update project in the underlying data source."""
        return self.data_source.update_project(project_data)
    
    def sync_from_source(self, source_adapter):
        """Sync data from another source (e.g., PostgreSQL to IndexedDB)."""
        # Implementation would handle syncing between sources
        pass


# For the demo, we'll create a synthetic data provider that mimics
# what the universal adapter would do
class SyntheticDataProvider:
    """Provides synthetic data for demo purposes."""
    
    @staticmethod
    def get_demo_projects():
        """Generate synthetic project data."""
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
    
    @staticmethod
    def get_demo_project_details(project_name):
        """Generate synthetic project details."""
        statuses = ['completed', 'in-progress', 'todo', 'blocked', 'review']
        priorities = ['critical', 'high', 'medium', 'low']
        categories = ['development', 'testing', 'documentation', 'research', 'maintenance', 'design']
        
        total_tasks = random.randint(10, 50)
        
        # Generate status distribution
        status_counts = {}
        remaining = total_tasks
        for status in statuses[:-1]:
            if remaining <= 0:
                break
            count = random.randint(0, min(remaining, int(total_tasks * 0.4)))
            status_counts[status] = count
            remaining -= count
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


# Example usage of the universal adapter concept
def create_universal_adapter(is_demo=False):
    """
    Factory function to create the appropriate adapter.
    
    Args:
        is_demo (bool): If True, returns synthetic data provider for demo
                       If False, would return PostgreSQL adapter for real data
    """
    if is_demo:
        return SyntheticDataProvider
    else:
        # In a real implementation, this would return a PostgreSQL adapter
        # with actual database connection
        pass