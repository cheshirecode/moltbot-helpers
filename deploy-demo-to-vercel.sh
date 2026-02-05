#!/bin/bash
# Deploy OpenClaw Demo to Vercel

set -e  # Exit on any error

echo "🚀 Deploying OpenClaw Demo to Vercel..."

# Change to the demo directory
cd /home/fred/projects/moltbot-helpers/demo-dashboard

# Verify we're logged into Vercel
echo "Checking Vercel login status..."
if ! vercel whoami; then
    echo "❌ Not logged into Vercel. Please run: vercel login"
    exit 1
fi

echo "✅ Successfully authenticated with Vercel"

# Deploy to Vercel
echo "📦 Building and deploying to Vercel..."
vercel --prod --yes

echo ""
echo "🎉 Deployment completed!"
echo "🌐 Your demo is now live at: $(vercel url)"
echo ""
echo "💡 To redeploy in the future, simply run this script again or:"
echo "   cd demo-dashboard && vercel --prod"