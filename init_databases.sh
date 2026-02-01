#!/bin/bash
# init_databases.sh - Initialize empty databases for moltbot-helpers

set -e

echo "Initializing empty databases..."

# Create data directory if it doesn't exist
mkdir -p /app/data/_openclaw

# Initialize empty databases with proper schema (if needed)
# For now, we just create empty files, but the tools will initialize schemas on first use

# Create empty database files
touch /app/data/_openclaw/family-planning.db
touch /app/data/_openclaw/project-tracker.db  
touch /app/data/_openclaw/seek.db
touch /app/data/_openclaw/knowledge-graph.db
touch /app/data/_openclaw/memory-enhancements.db
touch /app/data/_openclaw/triggers.db

echo "Empty databases initialized at /app/data/_openclaw/"

# Optionally, run a quick test to ensure tools can access the databases
echo "Testing tools access..."
python -c "
import sqlite3
import os

dbs = [
    '/app/data/_openclaw/family-planning.db',
    '/app/data/_openclaw/project-tracker.db',
    '/app/data/_openclaw/seek.db',
    '/app/data/_openclaw/knowledge-graph.db',
    '/app/data/_openclaw/memory-enhancements.db',
    '/app/data/_openclaw/triggers.db'
]

for db in dbs:
    if os.path.exists(db):
        print(f'✓ {os.path.basename(db)} exists')
        conn = sqlite3.connect(db)
        conn.close()
    else:
        print(f'✗ {os.path.basename(db)} missing')
"

echo "Initialization complete!"