#!/usr/bin/env python3
"""
Generic Project Tracker CLI (pt)

Manages tasks, roadmap items, bugs, features across different projects.
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime

DATABASE_PATH = os.path.expanduser("~/projects/_openclaw/project-tracker.db")

def get_connection():
    """Establish a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_PATH)
    # Use row_factory to get results as dictionaries
    conn.row_factory = sqlite3.Row
    return conn

def list_entries(project, category=None, priority=None, status=None, tags=None):
    """List entries for a specific project, optionally filtered."""
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM entries WHERE project = ?"
    params = [project]

    if category:
        query += " AND category = ?"
        params.append(category)
    if priority:
        query += " AND priority = ?"
        params.append(priority)
    if status:
        query += " AND status = ?"
        params.append(status)
    if tags:
        # Assuming tags are stored as a comma-separated string
        query += " AND tags LIKE ?"
        params.append(f'%{tags}%')

    query += " ORDER BY created_date DESC, priority ASC" # Prioritize critical/newer

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print(f"No entries found for project '{project}'.")
        return

    print(f"\nEntries for project '{project}':")
    print("-" * 80)
    for row in rows:
        print(f"ID: {row['id']}")
        print(f"Category: {row['category']}")
        print(f"Priority: {row['priority']}")
        print(f"Status: {row['status']}")
        print(f"Title: {row['title']}")
        print(f"Description: {row['description'][:100]}{'...' if len(row['description']) > 100 else ''}") # Truncate description
        print(f"Tags: {row['tags']}")
        print(f"Created: {row['created_date']}, Updated: {row['updated_date']}")
        print("-" * 80)


def add_entry(project, category, title, description="", priority=None, impact=None, tech_debt_level=None, tags=None):
    """Add a new entry to the database."""
    conn = get_connection()
    cursor = conn.cursor()

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Convert tags list to a comma-separated string if provided
    tags_str = ",".join(tags) if tags else None

    cursor.execute("""
        INSERT INTO entries (
            project, category, title, description, priority, impact, tech_debt_level,
            created_date, updated_date, tags
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (project, category, title, description, priority, impact, tech_debt_level, now_str, now_str, tags_str))

    conn.commit()
    entry_id = cursor.lastrowid
    conn.close()

    print(f"Added new entry to '{project}' (ID: {entry_id}).")


def update_entry(entry_id, status=None, updated_date=None):
    """Update an existing entry's status."""
    conn = get_connection()
    cursor = conn.cursor()

    if updated_date is None:
        updated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Build the update query dynamically based on provided arguments
    updates = []
    params = []
    if status is not None:
        updates.append("status = ?")
        params.append(status)
    updates.append("updated_date = ?")
    params.append(updated_date)

    if not updates:
        print("No fields to update.")
        return

    query = f"UPDATE entries SET {', '.join(updates)} WHERE id = ?"
    params.append(entry_id)

    cursor.execute(query, params)
    conn.commit()
    conn.close()

    print(f"Updated entry ID {entry_id}.")


def get_entry(entry_id):
    """Retrieve a single entry by its ID."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        print(f"No entry found with ID {entry_id}.")
        return

    print("\nEntry Details:")
    print("-" * 80)
    print(f"ID: {row['id']}")
    print(f"Project: {row['project']}")
    print(f"Category: {row['category']}")
    print(f"Priority: {row['priority']}")
    print(f"Status: {row['status']}")
    print(f"Title: {row['title']}")
    print(f"Description: {row['description']}")
    print(f"Impact: {row['impact']}")
    print(f"Tech Debt Level: {row['tech_debt_level']}")
    print(f"Tags: {row['tags']}")
    print(f"Created: {row['created_date']}, Updated: {row['updated_date']}")
    print("-" * 80)


def search_entries(query, project=None):
    """Search for entries by title or description."""
    conn = get_connection()
    cursor = conn.cursor()

    sql_query = """
        SELECT * FROM entries
        WHERE (title LIKE ? OR description LIKE ?)
    """
    params = [f'%{query}%', f'%{query}%']

    if project:
        sql_query += " AND project = ?"
        params.append(project)

    sql_query += " ORDER BY created_date DESC, priority ASC"

    cursor.execute(sql_query, params)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print(f"No entries found matching '{query}'.")
        return

    print(f"\nSearch results for '{query}':")
    if project:
        print(f"(Project: {project})")
    print("-" * 80)
    for row in rows:
        print(f"ID: {row['id']} (Project: {row['project']})")
        print(f"Category: {row['category']}")
        print(f"Priority: {row['priority']}")
        print(f"Status: {row['status']}")
        print(f"Title: {row['title']}")
        print(f"Description: {row['description'][:100]}{'...' if len(row['description']) > 100 else ''}")
        print(f"Tags: {row['tags']}")
        print(f"Created: {row['created_date']}, Updated: {row['updated_date']}")
        print("-" * 80)


def main():
    parser = argparse.ArgumentParser(description="Generic Project Tracker CLI")
    parser.add_argument("--project", "-p", required=True, help="Project name (e.g., frontend-ai-template)")

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # List command
    parser_list = subparsers.add_parser('list', help='List entries')
    parser_list.add_argument("--category", help="Filter by category (e.g., roadmap, bug)")
    parser_list.add_argument("--priority", help="Filter by priority (e.g., critical, high)")
    parser_list.add_argument("--status", help="Filter by status (e.g., new, in_progress)")
    parser_list.add_argument("--tags", help="Filter by tags (comma-separated)")

    # Add command
    parser_add = subparsers.add_parser('add', help='Add a new entry')
    parser_add.add_argument("--category", "-c", required=True, help="Category (e.g., roadmap, todo, bug, feature)")
    parser_add.add_argument("--title", "-t", required=True, help="Title of the entry")
    parser_add.add_argument("--description", "-d", help="Description of the entry")
    parser_add.add_argument("--priority", help="Priority (e.g., critical, high, medium, low)")
    parser_add.add_argument("--impact", help="Impact level (e.g., critical, high, medium, low)")
    parser_add.add_argument("--tech-debt-level", "--td", help="Tech debt level (e.g., high, medium, low)")
    parser_add.add_argument("--tags", nargs='+', help="Tags for the entry (space-separated)")

    # Update command
    parser_update = subparsers.add_parser('update', help='Update an entry')
    parser_update.add_argument("entry_id", type=int, help="ID of the entry to update")
    parser_update.add_argument("--status", help="New status (e.g., in_progress, completed)")

    # Get command
    parser_get = subparsers.add_parser('get', help='Get a specific entry by ID')
    parser_get.add_argument("entry_id", type=int, help="ID of the entry to retrieve")

    # Search command
    parser_search = subparsers.add_parser('search', help='Search entries by title/description')
    parser_search.add_argument("query", help="Search query string")
    # Optionally allow project filter for search too
    parser_search.add_argument("--project", "-p_search", help="Filter search by project (optional, overrides --project if used here)")


    args = parser.parse_args()

    if args.command == 'list':
        list_entries(args.project, args.category, args.priority, args.status, args.tags)
    elif args.command == 'add':
        add_entry(
            args.project, args.category, args.title, args.description,
            args.priority, args.impact, args.tech_debt_level, args.tags
        )
    elif args.command == 'update':
        update_entry(args.entry_id, status=args.status)
    elif args.command == 'get':
        get_entry(args.entry_id)
    elif args.command == 'search':
        # Use project from search-specific arg if provided, otherwise use the main one
        search_project = args.project if not hasattr(args, 'project_search') or args.project_search is None else args.project_search
        search_entries(args.query, project=search_project)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()