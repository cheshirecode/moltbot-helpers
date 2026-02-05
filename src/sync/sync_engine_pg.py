"""
PostgreSQL Memory-Database Synchronization Engine

This module provides functions to synchronize between memory files and the PostgreSQL database.
"""

import psycopg2
import os
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import json


class MemorySync:
    def __init__(self, db_host: str = None, db_port: int = None, db_name: str = None, db_user: str = None, db_password: str = None):
        self.db_host = db_host or os.environ.get("PT_DB_HOST", "localhost")
        self.db_port = db_port or int(os.environ.get("PT_DB_PORT", 5433))
        self.db_name = db_name or os.environ.get("PT_DB_NAME", "financial_analysis")
        self.db_user = db_user or os.environ.get("PT_DB_USER", "finance_user")
        self.db_password = db_password or os.environ.get("PT_DB_PASSWORD", "secure_finance_password")
        
    def get_connection(self):
        """Establish a connection to the PostgreSQL database."""
        conn = psycopg2.connect(
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            user=self.db_user,
            password=self.db_password
        )
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
        """Sync tasks from a memory file to the PostgreSQL database."""
        tasks = self.extract_tasks_from_memory(memory_file_path)
        conn = self.get_connection()
        cursor = conn.cursor()
        
        synced_count = 0
        
        for task in tasks:
            # Check if a similar task already exists in the database
            cursor.execute("""
                SELECT id FROM project_tracker 
                WHERE project = %s AND title = %s AND description LIKE %s
            """, (project_name, task['title'], f"%{task['description'][:50]}%"))
            
            existing = cursor.fetchone()
            
            if not existing:
                # Insert new task
                now_str = datetime.now()
                tags_json = json.dumps(['synced-from-memory', task['source_file']])
                
                cursor.execute("""
                    INSERT INTO project_tracker (
                        project, category, title, description, status, 
                        created_date, updated_date, tags
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    project_name,
                    'task',  # Default category for memory-extracted tasks
                    task['title'],
                    task['description'],
                    task['status'],
                    now_str,
                    now_str,
                    tags_json
                ))
                synced_count += 1
            else:
                # Update status if different
                cursor.execute("""
                    UPDATE project_tracker 
                    SET status = %s, updated_date = %s
                    WHERE id = %s
                """, (
                    task['status'],
                    datetime.now(),
                    existing[0]  # ID is first column in fetched result
                ))
                synced_count += 1
        
        conn.commit()
        conn.close()
        
        return synced_count
    
    def sync_all_memory_files(self, memory_dir: str = "memory", project_name: str = "openclaw") -> Dict[str, int]:
        """Sync all memory files in a directory to the PostgreSQL database."""
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
            SELECT * FROM project_tracker 
            WHERE project = %s
            ORDER BY created_date DESC
        """, (project_name,))
        
        entries = cursor.fetchall()
        # Get column names
        col_names = [desc[0] for desc in cursor.description]
        conn.close()
        
        if not entries:
            print(f"No entries found for project '{project_name}'")
            return 0
            
        # Write to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# Project Tracker Export - {project_name}\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for entry in entries:
                # Convert tuple to dict using column names
                entry_dict = {col_names[i]: entry[i] for i in range(len(col_names))}
                f.write(f"## Entry ID: {entry_dict['id']}\n")
                f.write(f"- **Title:** {entry_dict['title']}\n")
                f.write(f"- **Category:** {entry_dict['category']}\n")
                f.write(f"- **Status:** {entry_dict['status']}\n")
                f.write(f"- **Priority:** {entry_dict.get('priority', 'medium')}\n")
                f.write(f"- **Description:** {entry_dict['description']}\n")
                f.write(f"- **Created:** {entry_dict['created_date']}\n")
                f.write(f"- **Updated:** {entry_dict['updated_date']}\n")
                f.write("\n")
        
        return len(entries)
    
    def check_consistency(self, project_name: str = "openclaw") -> Dict:
        """Check consistency between memory files and database."""
        import glob
        
        # Get all entries from database for the project
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM project_tracker 
            WHERE project = %s
        """, (project_name,))
        
        db_entries = cursor.fetchall()
        # Get column names
        col_names = [desc[0] for desc in cursor.description]
        conn.close()
        
        # Convert tuples to dicts for easier access
        db_entries_dict = []
        for entry in db_entries:
            entry_dict = {col_names[i]: entry[i] for i in range(len(col_names))}
            db_entries_dict.append(entry_dict)
        
        # Get tasks from all memory files
        memory_files = glob.glob("memory/*.md")
        all_memory_tasks = []
        
        for memory_file in memory_files:
            tasks = self.extract_tasks_from_memory(memory_file)
            all_memory_tasks.extend(tasks)
        
        # Compare and report inconsistencies
        db_titles = {entry['title'].lower().strip() for entry in db_entries_dict}
        memory_titles = {task['title'].lower().strip() for task in all_memory_tasks}
        
        missing_in_db = memory_titles - db_titles
        missing_in_memory = db_titles - memory_titles
        
        return {
            'missing_in_db': list(missing_in_db),
            'missing_in_memory': list(missing_in_memory),
            'db_count': len(db_entries_dict),
            'memory_count': len(all_memory_tasks)
        }