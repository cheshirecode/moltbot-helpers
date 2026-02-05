#!/bin/bash
# Docker-based launch script for OpenClaw Main Dashboard UI

echo "🚀 Starting OpenClaw Main Dashboard UI in Docker..."
echo "🌐 Dashboard available at: http://localhost:5000/"

# Run the main dashboard API server in Docker container
docker run --rm -p 5000:5000 \
  -v /home/fred/projects/_openclaw:/data/_openclaw \
  -v /home/fred/.openclaw/workspace:/workspace \
  -e PT_DB_HOST=host.docker.internal \
  -e PT_DB_PORT=5433 \
  -e PT_DB_NAME=financial_analysis \
  -e PT_DB_USER=finance_user \
  -e PT_DB_PASSWORD=secure_finance_password \
  -w /app \
  moltbot-helpers-quick bash -c "pip install --user flask psycopg2-binary && python -m flask run --host=0.0.0.0 --port=5000"