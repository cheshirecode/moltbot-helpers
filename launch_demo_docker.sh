#!/bin/bash
# Docker-based launch script for OpenClaw Demo Dashboard

echo "🚀 Starting OpenClaw Public Demo Dashboard in Docker..."
echo "🌐 Demo available at: http://localhost:5001/demo"

# Run the demo dashboard in Docker container
docker run --rm -p 5001:5001 \
  -v /home/fred/projects/_openclaw:/data/_openclaw \
  -v /home/fred/projects/moltbot-helpers:/workspace/moltbot-helpers \
  -e DATA_DIR=/data \
  -e WORKSPACE_DIR=/workspace \
  moltbot-helpers-quick bash -c "pip install --user flask && cd /workspace/moltbot-helpers && python demo_dashboard.py"