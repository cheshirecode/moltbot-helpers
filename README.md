# moltbot-helpers

Production-ready PostgreSQL-powered CLI tools for Moltbot/OpenClaw systems: `pt_pg` (project tracker), `seek_pg` (semantic search), `fp_pg` (family planner), `md2pg` (markdown processor), `gc` (Google Calendar), `integrate` (unified interface), `backup` (backup utility), `sync` (synchronization), and `service-manager` (process management).

## PostgreSQL-Powered Architecture

This suite now uses PostgreSQL as the primary data store for enhanced performance, reliability, and advanced features.

### PostgreSQL Tools (Recommended)

- `pt_pg` - PostgreSQL Project Tracker
- `seek_pg` - PostgreSQL Semantic Search Engine  
- `fp_pg` - PostgreSQL Family Planner
- `md2pg` - Markdown to PostgreSQL Processor

### Legacy Tools (Deprecated)

- `pt` - SQLite Project Tracker (deprecated)
- `seek` - SQLite Semantic Search Engine (deprecated)
- `fp` - SQLite Family Planner (deprecated)

> **Important**: New installations should use the PostgreSQL versions. Legacy tools will be removed in future releases.

## Production Deployment

### Docker Deployment (Recommended for Production)

For production environments, it's strongly recommended to run all tools in Docker containers with externalized data sources for security and isolation.

```bash
# Build the production Docker image
cd ~/projects/moltbot-helpers
docker build -f Dockerfile.production -t moltbot-helpers:production .

# Or use the quick build for development/testing
docker build -f Dockerfile.quick -t moltbot-helpers:latest .
```

### Running in Production

```bash
# Run with externalized data sources (recommended)
docker run --rm \
  -v /path/to/production-data:/data/_openclaw \
  -v /path/to/workspace:/workspace \
  moltbot-helpers:latest pt_pg --project openclaw list

# Using aliases for convenience (add to .shell_common or similar):
alias pt_pg='docker run --rm -v /path/to/production-data:/data/_openclaw -v /path/to/workspace:/workspace moltbot-helpers:latest pt_pg'
alias fp_pg='docker run --rm -v /path/to/production-data:/data/_openclaw -v /path/to/workspace:/workspace moltbot-helpers:latest fp_pg'
alias seek_pg='docker run --rm -v /path/to/production-data:/data/_openclaw -v /path/to/workspace:/workspace moltbot-helpers:latest seek_pg'
alias md2pg='docker run --rm -v /path/to/production-data:/data/_openclaw -v /path/to/workspace:/workspace moltbot-helpers:latest md2pg'
```

## Core PostgreSQL Tools

### pt_pg — PostgreSQL Project Tracker

Track and manage projects, tasks, and roadmap items in a PostgreSQL database.

```bash
pt_pg list                    # List all tasks
pt_pg --project openclaw list # List tasks for specific project
pt_pg add "New task" --project openclaw --priority high --category dev
pt_pg update 123 --status completed  # Update task status
pt_pg search "query"          # Search tasks
```

Environment variables:
- `PT_DB_HOST`: PostgreSQL host (default: localhost)
- `PT_DB_PORT`: PostgreSQL port (default: 5433)
- `PT_DB_NAME`: Database name (default: financial_analysis)
- `PT_DB_USER`: Database user (default: finance_user)
- `PT_DB_PASSWORD`: Database password (default: secure_finance_password)

### seek_pg — PostgreSQL Semantic Search

Index local files and search with hybrid semantic + full-text search using PostgreSQL.

```bash
seek_pg search "query"        # Hybrid search
seek_pg status               # Show index info
seek_pg reindex              # Force full reindex
```

Environment variables:
- Same as pt_pg (uses the same PostgreSQL connection)

### fp_pg — PostgreSQL Family Planner

Query and update the family PostgreSQL database.

```bash
fp_pg tasks          # Show open tasks
fp_pg balances       # Financial balances
fp_pg search <term>  # Search across all tables
```

Environment variables:
- Same as pt_pg (uses the same PostgreSQL connection)

### md2pg — Markdown to PostgreSQL Processor

Process markdown files and convert them to PostgreSQL database entries.

```bash
# Process a single file
md2pg import-file /path/to/file.md --project myproject

# Process a directory
md2pg import-dir /path/to/dir --project myproject

# Process from stdin
echo '# My Task' | md2pg process --project myproject --title "From stdin"
```

### integrate — Unified Interface

Cross-reference and integrate data between different systems.

```bash
integrate cross-ref "query"     # Cross-reference between systems
integrate recommendations       # Get recommendations based on current state
integrate project-context       # Get context about projects
integrate status                # Show integration status
```

### backup — Backup Utility

Create and manage backups of Moltbot/OpenClaw systems.

```bash
backup create                 # Create a backup
backup list                   # List available backups
backup restore <backup-name>  # Restore from a backup
backup info                   # Show backup information
```

### gc — Google Calendar

Perform CRUD operations against Google Calendar.

```bash
gc list-calendars           # List all available calendars
gc list-events              # List events from a calendar
gc create --summary "Title" --start "2026-02-01T10:00:00" --end "2026-02-01T11:00:00"  # Create new event
```

### sync — Synchronization Tool

Synchronize and verify consistency between memory files and databases.

```bash
sync check                    # Check consistency between memory and database
sync sync                     # Sync memory files to database
```

### service-manager — Process Management

Manage Moltbot/OpenClaw services and processes.

```bash
service-manager list          # List registered processes
service-manager status        # Show service status
```

### lookup — Documentation Lookup

Quickly look up documentation and information about the system.

```bash
lookup tools                  # Get information about tools
lookup <topic>                # Look up specific topic
```

## Security Best Practices

- All tools run in isolated Docker containers with non-root user execution
- Data sources are externalized via volume mounts
- No credentials are stored in the container image
- Use environment-specific credential management for production
- PostgreSQL connections use secure authentication

## Production Requirements

- Docker 20.10 or later
- PostgreSQL 13 or later (for PostgreSQL tools)
- Sufficient disk space for database files and indexed content
- Appropriate file permissions on mounted volumes
- Network access for external APIs (if using Google Calendar, etc.)

## PostgreSQL Migration Complete

As of February 2026, all tools have been successfully migrated from SQLite to PostgreSQL:

- ✅ All data migrated to PostgreSQL
- ✅ All functionality preserved
- ✅ Enhanced capabilities with PostgreSQL features
- ✅ All tools operational with PostgreSQL backend
- ✅ Legacy tools deprecated but still available for reference

## Task Management Dashboard

New web-based dashboard for visualizing tasks from PostgreSQL database:

- `ui/dashboard.html` - Main dashboard UI
- `ui/api.py` - Flask API backend
- `ui/start_server.sh` - Server startup script
- `ui/run_dashboard.py` - Auto-launch script with browser opening
- `launch_dashboard.sh` - Main project launch script
- Interactive charts and project visualization
- Real-time data from PostgreSQL project tracker

## Architecture

The tools are implemented as Python applications with CLI interfaces. Wrapper scripts provide clean command-line access without file extensions.

- `backup`, `integrate`, `lookup`, `pt_pg`, `fp_pg`, `seek_pg`, `md2pg`, `service-manager`, `sync` - Python wrapper scripts
- Core functionality in the `src/` directory
- Configuration via environment variables
- PostgreSQL databases for data persistence (with SQLite versions being phased out)