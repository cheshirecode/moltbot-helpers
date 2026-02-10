#!/bin/bash
# demo-environment/scripts/reset_demo.sh

echo "🔄 Resetting OpenClaw Demo Environment..."
echo ""

# Change to the demo environment directory
cd "$(dirname "$0")/.." || exit

echo "📁 Working directory: $(pwd)"
echo ""

# Remove any temporary files or logs
find . -name "*.log" -delete 2>/dev/null || true
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name "*_cache" -delete 2>/dev/null || true

# Verify original files exist
if [ ! -f "original_data/synthetic_data.json" ]; then
    echo "⚠️  Warning: Original data not found, recreating from backup..."
    cp data/synthetic_data.json original_data/synthetic_data.json 2>/dev/null || true
fi

# Restore original synthetic data
if [ -f "original_data/synthetic_data.json" ]; then
    cp original_data/synthetic_data.json data/synthetic_data.json
    echo "✅ Restored original synthetic data"
else
    echo "⚠️  Warning: Could not restore original data"
fi

# Reset any mock service states
echo "🧹 Cleaning up mock services..."
pkill -f "google_api_mock" 2>/dev/null || true
pkill -f "github_api_mock" 2>/dev/null || true

echo ""
echo "✅ Demo environment reset to clean state"
echo "💡 Run 'start_demo.sh' to start the demo again"