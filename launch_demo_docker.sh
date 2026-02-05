#!/bin/bash
# Docker-based launch script for OpenClaw Demo Server

echo "🚀 Starting OpenClaw Public Demo Server in Docker..."
echo "🌐 Demo available at: http://localhost:5001/demo"

# Run the demo server in Docker container
docker run --rm -p 5001:5001 \
  -v /home/fred/projects/_openclaw:/data/_openclaw \
  -v /home/fred/.openclaw/workspace:/workspace \
  -w /app \
  moltbot-helpers-quick bash -c "pip install --user flask && python /workspace/demo_server.py"