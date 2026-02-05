#!/bin/bash
# Environment setup script for OpenClaw tools to connect to k8s PostgreSQL

# Set environment variables to connect to PostgreSQL in k8s cluster
export PT_DB_HOST=host.docker.internal
export PT_DB_PORT=5433
export PT_DB_NAME=financial_analysis
export PT_DB_USER=finance_user
export PT_DB_PASSWORD=secure_finance_password

echo "Environment variables set for connecting to k8s PostgreSQL:"
echo "  PT_DB_HOST=$PT_DB_HOST"
echo "  PT_DB_PORT=$PT_DB_PORT"
echo "  PT_DB_NAME=$PT_DB_NAME"
echo "  PT_DB_USER=$PT_DB_USER"
echo "  PT_DB_PASSWORD=***********"

echo ""
echo "You can now run tools like:"
echo "  docker run --rm -v /home/fred/projects/_openclaw:/data/_openclaw -v /home/fred/.openclaw/workspace:/workspace -e PT_DB_HOST=\$PT_DB_HOST -e PT_DB_PORT=\$PT_DB_PORT moltbot-helpers-quick pt_pg --project=openclaw list"