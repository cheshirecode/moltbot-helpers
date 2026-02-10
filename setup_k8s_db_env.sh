#!/bin/bash
# Environment setup script for OpenClaw tools to connect to k8s PostgreSQL

# Set environment variables to connect to PostgreSQL in k8s cluster
export PT_DB_HOST=host.docker.internal
export PT_DB_PORT=5433
export PT_DB_NAME=openclaw
export PT_DB_USER=postgres
export PT_DB_PASS=postgres

# Start port-forward if not already running
if ! pgrep -f "kubectl port-forward.*postgres-db" > /dev/null; then
    echo "Starting port-forward to PostgreSQL service..."
    kubectl port-forward -n openclaw-services svc/postgres-db 5433:5432 > /tmp/k8s-portforward.log 2>&1 &
    sleep 3
fi

echo "Environment variables set for connecting to k8s PostgreSQL:"
echo "  PT_DB_HOST=$PT_DB_HOST"
echo "  PT_DB_PORT=$PT_DB_PORT"
echo "  PT_DB_NAME=$PT_DB_NAME"
echo "  PT_DB_USER=$PT_DB_USER"
echo "  PT_DB_PASS=***********"

echo ""
echo "You can now run tools like:"
echo "  docker run --rm -v /home/fred/projects/_openclaw:/data/_openclaw -v /home/fred/.openclaw/workspace:/workspace -e PT_DB_HOST=\$PT_DB_HOST -e PT_DB_PORT=\$PT_DB_PORT moltbot-helpers-quick pt_pg --project=openclaw list"