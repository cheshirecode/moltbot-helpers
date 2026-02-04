# Moltbot Helpers Docker Setup - Security-First Approach

This repository contains helper tools for OpenClaw/Moltbot systems, including:

- `pt` - Project Tracker CLI
- `fp` - Family Planner CLI  
- `seek` - Semantic Search Engine
- `integrate` - Unified Interface
- `backup` - Backup Utility
- `sync` - Synchronization Service
- `service-manager` - Process Manager
- `lookup` - Documentation Lookup

## Security Features

The Docker image implements several security features:
- Non-root user execution (runs as `moltbot` user)
- Isolated environment with limited host access
- Externalized data sources for secure data handling
- Minimal attack surface with only required dependencies

## Docker Setup with External Data Sources

Build the Docker image with externalizable data sources:

```bash
# Use Dockerfile.quick for externalized data sources with security enhancements
docker build -f Dockerfile.quick -t moltbot-helpers-quick .
```

## Running with External Data Sources

The Docker image is designed to work with external data sources mounted at runtime for persistence:

```bash
# Basic usage with external data sources (runs as non-root user)
docker run -it \
  -v /path/to/my/data:/data/_openclaw \
  -v /path/to/my/workspace:/workspace \
  moltbot-helpers-quick /bin/bash

# Example with current system paths
docker run -it \
  -v /home/fred/projects/_openclaw:/data/_openclaw \
  -v /home/fred/.openclaw/workspace:/workspace \
  moltbot-helpers-quick /bin/bash
```

## Available CLI Tools

The following CLI tools will be available globally in the container:
- `pt` - Project Tracker
- `fp` - Family Planner
- `seek` - Semantic Search
- `integrate` - Cross-reference tool
- `backup` - Backup utility
- `service-manager` - Service management
- `sync` - Synchronization tool
- `lookup` - Information lookup

## Using the Tools with External Data

Once the container is running with mounted volumes, you can use the tools directly with your external data:

```bash
# List project tracker entries from external database
pt --project openclaw list

# Query family planning data from external database
fp tasks

# Perform semantic search on external memory files
seek query "recent tasks"

# Run cross-references between external data sources
integrate cross-ref --help
```

## Data Source Mount Points

The container expects data sources at these locations:
- `/data/_openclaw` - Database files (family-planning.db, project-tracker.db, seek.db, etc.)
- `/workspace` - Memory markdown files (MEMORY.md, daily memory files in /workspace/memory/)

## Environment Variables

The container uses these environment variables for configuration:
- `DATA_DIR=/data` (default) - Base directory for databases
- `WORKSPACE_DIR=/workspace` (default) - Base directory for memory files

These can be overridden at runtime if needed:
```bash
docker run -e DATA_DIR=/mydata -e WORKSPACE_DIR=/myworkspace -v /path/to/data:/mydata -v /path/to/workspace:/myworkspace moltbot-helpers-quick
```

## Persistence and Reusability

By mounting external data sources, you can:
- Preserve data across container runs and rebuilds
- Share data between different container instances
- Backup and restore data easily
- Use the same data sources with different versions of the tools

## Quick Command Examples

```bash
# Run a single command with external data
docker run --rm \
  -v /home/fred/projects/_openclaw:/data/_openclaw \
  -v /home/fred/.openclaw/workspace:/workspace \
  moltbot-helpers-quick pt list

# Start an interactive session with your data
docker run -it \
  -v /home/fred/projects/_openclaw:/data/_openclaw \
  -v /home/fred/.openclaw/workspace:/workspace \
  moltbot-helpers-quick /bin/bash

# Run a specific tool command
docker run --rm \
  -v /home/fred/projects/_openclaw:/data/_openclaw \
  -v /home/fred/.openclaw/workspace:/workspace \
  moltbot-helpers-quick seek query "security audit"
```

## Architecture

All tools operate locally with no external dependencies:
- SQLite databases for persistence
- Local file system for memory and configuration
- Vector databases for semantic search
- Pure Python implementation for portability

The Docker image supports external data sources for maximum flexibility while maintaining full functionality of all tools.