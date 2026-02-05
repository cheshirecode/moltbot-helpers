#!/usr/bin/env python3
"""
Markdown to PostgreSQL Processor CLI (md2pg)

Consumes markdown files and converts them to PostgreSQL database entries based on project categorization.
"""

import argparse
import json
import os
import psycopg2
import psycopg2.extras
import re
import sys
from datetime import datetime
from pathlib import Path
import markdown
from bs4 import BeautifulSoup


# Use environment variables for PostgreSQL connection
DB_HOST = os.environ.get("PT_DB_HOST", "localhost")
DB_PORT = int(os.environ.get("PT_DB_PORT", 5433))
DB_NAME = os.environ.get("PT_DB_NAME", "financial_analysis")
DB_USER = os.environ.get("PT_DB_USER", "finance_user")
DB_PASSWORD = os.environ.get("PT_DB_PASSWORD", "secure_finance_password")


def get_connection():
    """Establish a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        sys.exit(1)


def extract_project_info(content):
    """Extract project information from markdown content."""
    # Look for project-related keywords or sections in the markdown
    project_patterns = [
        r'# Project: ([^\n]+)',
        r'Project: ([^\n]+)',
        r'# ([A-Za-z0-9_-]+) Project',
        r'## Project ([A-Za-z0-9_-]+)'
    ]
    
    for pattern in project_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    # If no explicit project found, return a default
    return "general"


def extract_tasks_from_markdown(content):
    """Extract tasks/todo items from markdown content."""
    tasks = []
    
    # Look for TODO patterns
    todo_pattern = r'(TODO|FIXME|BUG|ISSUE)[:\-\s]*([^\n]+)'
    for match in re.finditer(todo_pattern, content, re.IGNORECASE):
        task_description = match.group(2).strip()
        task_type = match.group(1).upper()
        
        # Determine priority based on type
        priority_map = {
            'BUG': 'critical',
            'FIXME': 'high',
            'ISSUE': 'medium',
            'TODO': 'low'
        }
        priority = priority_map.get(task_type, 'medium')
        
        tasks.append({
            'title': f"[{task_type}] {task_description}",
            'description': f"Extracted from markdown: {task_description}",
            'priority': priority,
            'category': 'todo',
            'status': 'new'
        })
    
    # Look for checklist items
    checklist_pattern = r'^\s*[\*\-\+]\s+\[([ x])\]\s+(.+)$'
    for line in content.split('\n'):
        match = re.match(checklist_pattern, line)
        if match:
            checked = match.group(1) == 'x'
            item = match.group(2).strip()
            
            status = 'completed' if checked else 'new'
            category = 'todo'
            
            tasks.append({
                'title': item,
                'description': f"Checklist item from markdown: {item}",
                'priority': 'medium',
                'category': category,
                'status': status
            })
    
    return tasks


def extract_sections_as_tasks(content):
    """Extract sections and subsections as potential tasks/features."""
    tasks = []
    
    # Look for markdown headers that might represent features or tasks
    header_pattern = r'^(#{1,6})\s+(.+)$'
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        match = re.match(header_pattern, line)
        if match:
            header_level = len(match.group(1))
            header_text = match.group(2).strip()
            
            # Skip top-level headers (likely document titles)
            if header_level <= 2:
                continue
                
            # Add as a potential feature/task
            tasks.append({
                'title': header_text,
                'description': f"Section extracted from markdown content near line {i+1}",
                'priority': 'medium',
                'category': 'feature',
                'status': 'new'
            })
    
    return tasks


def process_markdown_file(file_path, project_name=None):
    """Process a single markdown file and extract structured data."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract project info if not provided
    if not project_name:
        project_name = extract_project_info(content)
    
    # Extract tasks from markdown
    tasks = extract_tasks_from_markdown(content)
    tasks.extend(extract_sections_as_tasks(content))
    
    # Create a summary record for the file itself
    file_summary = {
        'title': f"Processed: {os.path.basename(file_path)}",
        'description': f"Markdown file processed: {file_path}\nExtracted {len(tasks)} potential tasks/features",
        'priority': 'low',
        'category': 'documentation',
        'status': 'completed'
    }
    
    return project_name, [file_summary] + tasks


def import_markdown_to_db(file_path, project_name=None):
    """Import a markdown file to PostgreSQL database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        project, tasks = process_markdown_file(file_path, project_name)
        
        imported_count = 0
        for task in tasks:
            now_str = datetime.now()
            tags_json = json.dumps(['imported-from-md', project.lower()])
            
            cursor.execute("""
                INSERT INTO project_tracker (
                    project, category, title, description, priority, 
                    created_date, updated_date, tags, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                project, task['category'], task['title'], task['description'],
                task['priority'], now_str, now_str, tags_json, task['status']
            ))
            
            entry_id = cursor.fetchone()[0]
            print(f"  Added task: {task['title']} (ID: {entry_id})")
            imported_count += 1
        
        conn.commit()
        print(f"Successfully imported {imported_count} entries from {file_path} to project '{project}'")
        
    except Exception as e:
        print(f"Error importing {file_path}: {e}")
        conn.rollback()
    finally:
        conn.close()


def import_directory_to_db(directory_path, project_name=None):
    """Import all markdown files from a directory to PostgreSQL database."""
    directory = Path(directory_path)
    md_files = list(directory.rglob("*.md"))  # Recursively find all .md files
    
    print(f"Found {len(md_files)} markdown files in {directory_path}")
    
    for md_file in md_files:
        print(f"Processing: {md_file}")
        import_markdown_to_db(str(md_file), project_name)


def main():
    parser = argparse.ArgumentParser(description="Markdown to PostgreSQL Processor (md2pg)")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Import single file command
    parser_import_file = subparsers.add_parser('import-file', help='Import a single markdown file to PostgreSQL')
    parser_import_file.add_argument('file_path', help='Path to the markdown file to import')
    parser_import_file.add_argument('--project', '-p', help='Project name to assign (optional)')
    
    # Import directory command
    parser_import_dir = subparsers.add_parser('import-dir', help='Import all markdown files from directory to PostgreSQL')
    parser_import_dir.add_argument('directory_path', help='Path to the directory containing markdown files')
    parser_import_dir.add_argument('--project', '-p', help='Project name to assign to all files (optional)')
    
    # Process content command (reads from stdin)
    parser_process = subparsers.add_parser('process', help='Process markdown content from stdin')
    parser_process.add_argument('--project', '-p', help='Project name to assign (optional)')
    parser_process.add_argument('--title', '-t', help='Title for the content', required=True)
    
    args = parser.parse_args()
    
    if args.command == 'import-file':
        if not os.path.exists(args.file_path):
            print(f"File not found: {args.file_path}")
            sys.exit(1)
        import_markdown_to_db(args.file_path, args.project)
    elif args.command == 'import-dir':
        if not os.path.exists(args.directory_path):
            print(f"Directory not found: {args.directory_path}")
            sys.exit(1)
        import_directory_to_db(args.directory_path, args.project)
    elif args.command == 'process':
        # Read markdown content from stdin
        content = sys.stdin.read()
        
        # Create a temporary file with the content
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Process the temporary file
            import_markdown_to_db(temp_file_path, args.project or extract_project_info(content))
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()