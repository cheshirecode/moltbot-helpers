#!/bin/bash
# demo-environment/scripts/start_demo.sh

echo "🚀 Starting OpenClaw Demo Environment..."
echo "⚠️  WARNING: This is an isolated demo environment with synthetic data."
echo "⚠️  No real systems or data will be accessed."
echo ""

# Set demo-specific environment variables
export OPENCLAW_DEMO_MODE=true
export OPENCLAW_CONFIG_PATH="./config/demo_config.yaml"
export OPENCLAW_DATA_PATH="./data/"

# Change to the demo environment directory
cd "$(dirname "$0")/.." || exit

echo "📁 Working directory: $(pwd)"
echo ""

# Verify required files exist
if [ ! -f "config/demo_config.yaml" ]; then
    echo "❌ Error: config/demo_config.yaml not found"
    exit 1
fi

if [ ! -f "data/synthetic_data.json" ]; then
    echo "❌ Error: data/synthetic_data.json not found"
    exit 1
fi

if [ ! -f "demo_agent.py" ]; then
    echo "❌ Error: demo_agent.py not found"
    exit 1
fi

echo "✅ All required files found"
echo ""

# Start the demo environment
echo "🎮 Starting demo agent..."
echo ""
echo "💡 TIP: Type 'help' once the agent starts for available commands"
echo "💡 TIP: Type 'quit' to exit the demo"
echo ""

python3 demo_agent.py --config ./config/demo_config.yaml

echo ""
echo "👋 Demo environment stopped. Thanks for trying OpenClaw!"