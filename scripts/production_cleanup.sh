#!/bin/bash
# production_cleanup.sh - Clean up moltbot-helpers for production deployment

set -e  # Exit on any error

echo "Starting moltbot-helpers production cleanup..."

# Remove development-specific files
echo "Removing development artifacts..."
rm -rf seek_env/  # Remove local Python environment
rm -rf .venv/     # Remove virtual environment if present
rm -f test_docker_external_sources.sh  # Remove test script
rm -f test_external_sources.sh  # Remove any other test files

# Remove cache files
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type f -name "*~" -delete 2>/dev/null || true

# Remove any temporary files
find . -type f -name "*.tmp" -delete 2>/dev/null || true
find . -type f -name "*.temp" -delete 2>/dev/null || true

# Create production configuration
echo "Creating production configuration..."

# Update pyproject.toml to production version
cp pyproject.toml.production pyproject.toml

# Create production-ready README
cp README.PRODUCTION README.md

# Create a production deployment guide
cat > PRODUCTION_DEPLOYMENT.md << 'EOF'
# Production Deployment Guide

## Prerequisites

- Docker 20.10+
- Sufficient disk space for databases
- Appropriate file permissions on host directories

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd moltbot-helpers
   ```

2. Build the production Docker image:
   ```bash
   docker build -f Dockerfile.production -t moltbot-helpers:production .
   ```

## Configuration

Mount your data directories when running the container:

```bash
# Create data directories on the host
mkdir -p /opt/moltbot/data/_openclaw
mkdir -p /opt/moltbot/workspace

# Run with mounted volumes
docker run --rm \
  -v /opt/moltbot/data:/data \
  -v /opt/moltbot/workspace:/workspace \
  moltbot-helpers:production
```

## Environment Variables

The following environment variables control the database paths:

- `PROJECT_TRACKER_DB_PATH`: Project tracker database path
- `FP_DB`: Family planning database path
- `SEEK_DB_PATH`: Seek database path

These are automatically set in the Docker image but can be overridden.

## Usage Examples

```bash
# Run project tracker
docker run --rm \
  -v /opt/moltbot/data:/data \
  -v /opt/moltbot/workspace:/workspace \
  moltbot-helpers:production pt --project openclaw list

# Run semantic search
docker run --rm \
  -v /opt/moltbot/data:/data \
  -v /opt/moltbot/workspace:/workspace \
  moltbot-helpers:production seek search "query"
```

## Security Notes

- The container runs as a non-root user (moltbot)
- Data is stored outside the container via volume mounts
- No credentials are stored in the container image
- Access credentials through mounted files or environment variables

## Updating

To update to a new version:

1. Pull the latest changes
2. Rebuild the Docker image
3. Restart containers with the new image
EOF

echo "Cleanup completed successfully!"
echo ""
echo "Files prepared for production:"
echo "- Production Dockerfile: Dockerfile.production"
echo "- Production pyproject.toml"
echo "- Updated README.md for production"
echo "- Production deployment guide: PRODUCTION_DEPLOYMENT.md"
echo ""
echo "To build the production image:"
echo "docker build -f Dockerfile.production -t moltbot-helpers:production ."