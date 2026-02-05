#!/bin/bash
# Start the task management dashboard API server

echo "Starting OpenClaw Task Management Dashboard API..."
echo "Connecting to PostgreSQL database..."
echo "Host: $PT_DB_HOST (default: localhost)"
echo "Port: $PT_DB_PORT (default: 5433)"
echo "Database: $PT_DB_NAME (default: financial_analysis)"
echo "User: $PT_DB_USER (default: finance_user)"
echo ""

cd /home/fred/projects/moltbot-helpers/ui

# Run the Flask API server
python3 api.py