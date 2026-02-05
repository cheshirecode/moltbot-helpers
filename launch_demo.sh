#!/bin/bash
# Launch script for OpenClaw Demo Server

echo "🚀 Starting OpenClaw Public Demo Server..."

# Activate the virtual environment and run the demo server
cd /home/fred/projects/moltbot-helpers
source .venv/bin/activate
python3 demo_server.py