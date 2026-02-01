"""
Memory-Database Synchronization Engine

This module provides functions to synchronize between memory files and the project tracker database.
"""

import sqlite3
import os
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class MemorySync:
    def __init__(self, db_path: str = "~/projects/_openclaw/project-tracker.db"):
        self.db_path = os.path.expanduser(db_path)
        
    def get_connection(self):
        """Establish a connection to the SQLite database."""
        conn = sqlite3.connect(self.db_path)
        # Use row_factory to get results as dictionaries
        conn.row_factory = sqlite3.Row
        return conn
    
    def extract_tasks_from_memory(self, memory_file_path: str) -> List[Dict]:
        """Extract project-related tasks from a memory file."""
        tasks = []
        
        with open(memory_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Look for patterns that indicate tasks or projects
        # Common patterns: numbered lists, bullet points with project/task keywords
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Look for completed tasks pattern like "1. **Completed Task** - Description"
            # Or patterns like "- Task completed: description"
            # Or patterns like "Task: task description"
            
            # Pattern for numbered tasks
            numbered_task_pattern = r'^\s*\d+\.\s*\*\*(.+?)\*\*\s*[-:]?\s*(.*)'
            numbered_match = re.match(numbered_task_pattern, line.strip())
            
            if numbered_match:
                title = numbered_match.group(1).strip()
                description = numbered_match.group(2).strip()
                
                # Determine if it's completed by looking for completion indicators
                status = 'completed' if any(word in title.lower() for word in ['completed', 'done', 'finished']) else 'new'
                
                # Look ahead for additional description in the next few lines
                for j in range(i+1, min(i+5, len(lines))):
                    next_line = lines[j].strip()
                    if next_line.startswith((' ', '\t')) or next_line.startswith('- '):
                        description += ' ' + next_line.strip()
                    else:
                        break
                        
                tasks.append({
                    'title': title,
                    'description': description,
                    'status': status,
                    'source_file': memory_file_path
                })
            
            # Pattern for bulleted tasks
            bullet_task_pattern = r'^\s*[-*]\s*(.+?)(?:\s*[-:]\s*(.*))?'
            bullet_match = re.match(bullet_task_pattern, line.strip())
            
            if bullet_match:
                title = bullet_match.group(1).strip()
                description = bullet_match.group(2).strip() if bullet_match.group(2) else ""
                
                # Determine status based on keywords
                status = 'new'
                combined_text = (title + ' ' + description).lower()
                if any(word in combined_text for word in ['completed', 'done', 'finished']):
                    status = 'completed'
                elif any(word in combined_text for word in ['in progress', 'working', 'started']):
                    status = 'in_progress'
                    
                # Look ahead for additional description in the next few lines
                for j in range(i+1, min(i+5, len(lines))):
                    next_line = lines[j].strip()
                    if next_line.startswith((' ', '\t')) or next_line.startswith('- '):
                        description += ' ' + next_line.strip()
                    else:
                        break
                        
                tasks.append({
                    'title': title,
                    'description': description,
                    'status': status,
                    'source_file': memory_file_path
                })
                
        return tasks
    
    def sync_memory_to_db(self, memory_file_path: str, project_name: str = "openclaw") -> int:
        """Sync tasks from a memory file to the database."""
        tasks = self.extract_tasks_from_memory(memory_file_path)
        conn = self.get_connection()
        cursor = conn.cursor()
        
        synced_count = 0
        
        for task in tasks:
            # Check if a similar task already exists in the database
            cursor.execute("""
                SELECT id FROM entries 
                WHERE project = ? AND title = ? AND description LIKE ?
            """, (project_name, task['title'], f"%{task['description'][:50]}%"))
            
            existing = cursor.fetchone()
            
            if not existing:
                # Insert new task
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("""
                    INSERT INTO entries (
                        project, category, title, description, status, created_date, updated_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    project_name,
                    'task',  # Default category for memory-extracted tasks
                    task['title'],
                    task['description'],
                    task['status'],
                    now_str,
                    now_str
                ))
                synced_count += 1
            else:
                # Update status if different
                cursor.execute("""
                    UPDATE entries 
                    SET status = ?, updated_date = ?
                    WHERE id = ?
                """, (
                    task['status'],
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    existing['id']
                ))
                synced_count += 1
        
        conn.commit()
        conn.close()
        
        return synced_count
    
    def sync_all_memory_files(self, memory_dir: str = "memory", project_name: str = "openclaw") -> Dict[str, int]:
        """Sync all memory files in a directory to the database."""
        import glob
        
        results = {}
        
        # Get all memory files
        memory_files = glob.glob(os.path.join(memory_dir, "*.md"))
        
        for memory_file in memory_files:
            try:
                count = self.sync_memory_to_db(memory_file, project_name)
                results[memory_file] = count
            except Exception as e:
                print(f"Error syncing {memory_file}: {str(e)}")
                results[memory_file] = 0
                
        return results
    
    def export_db_to_memory(self, project_name: str, output_file: str) -> int:
        """Export database entries for a project to a memory file."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM entries 
            WHERE project = ?
            ORDER BY created_date DESC
        """, (project_name,))
        
        entries = cursor.fetchall()
        conn.close()
        
        if not entries:
            print(f"No entries found for project '{project_name}'")
            return 0
            
        # Write to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# Project Tracker Export - {project_name}\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for entry in entries:
                f.write(f"## Entry ID: {entry['id']}\n")
                f.write(f"- **Title:** {entry['title']}\n")
                f.write(f"- **Category:** {entry['category']}\n")
                f.write(f"- **Status:** {entry['status']}\n")
                f.write(f"- **Priority:** {entry['priority']}\n")
                f.write(f"- **Description:** {entry['description']}\n")
                f.write(f"- **Created:** {entry['created_date']}\n")
                f.write(f"- **Updated:** {entry['updated_date']}\n")
                f.write("\n")
        
        return len(entries)
    
    def check_consistency(self, project_name: str = "openclaw") -> Dict:
        """Check consistency between memory files and database."""
        import glob
        
        # Get all entries from database for the project
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM entries 
            WHERE project = ?
        """, (project_name,))
        
        db_entries = cursor.fetchall()
        conn.close()
        
        # Get tasks from all memory files
        memory_files = glob.glob("memory/*.md")
        all_memory_tasks = []
        
        for memory_file in memory_files:
            tasks = self.extract_tasks_from_memory(memory_file)
            all_memory_tasks.extend(tasks)
        
        # Compare and report inconsistencies
        db_titles = {entry['title'].lower().strip() for entry in db_entries}
        memory_titles = {task['title'].lower().strip() for task in all_memory_tasks}
        
        missing_in_db = memory_titles - db_titles
        missing_in_memory = db_titles - memory_titles
        
        return {
            'missing_in_db': list(missing_in_db),
            'missing_in_memory': list(missing_in_memory),
            'db_count': len(db_entries),
            'memory_count': len(all_memory_tasks)
        }