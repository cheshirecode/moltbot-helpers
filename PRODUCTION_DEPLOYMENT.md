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
