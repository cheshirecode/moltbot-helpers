# moltbot-helpers

CLI tools for Moltbot/OpenClaw systems: `fp` (family planner), `seek` (local semantic search), `pt` (project tracker), `gc` (Google Calendar), `integrate` (unified interface), `backup` (backup utility), `sync` (synchronization), and `service-manager` (process management).

## Security-First Docker Approach

For security reasons, it's strongly recommended to run all tools in Docker containers with externalized data sources. This approach provides:

- Isolated execution environment
- No direct access to host credentials
- Better privilege separation
- Secure data handling

### Docker Installation (Recommended)

```bash
# Build the Docker image with externalized data sources
cd ~/projects/moltbot-helpers
docker build -f Dockerfile.quick -t moltbot-helpers-quick .

# Use the tools via Docker aliases (configured in .shell_common)
pt --project openclaw list
fp tasks
seek search "query"
```

### Local Installation (Use with caution)

⚠️ **Warning**: Local installation may expose credentials. Only use if necessary.

```bash
cd ~/projects/moltbot-helpers
uv venv
uv pip install -e .
```

## fp — Family Planner

Query and update the family SQLite database.

```bash
fp tasks          # Show open tasks
fp balances       # Financial balances
fp search <term>  # Search across all tables
fp add-task "Do something" P1 2026-03-01
```

Set `FP_DB` env var to override the database path (default: `~/clawd/memory/mox.db`).

## seek — Local Semantic Search

Index local files and SQLite databases, search with hybrid semantic + full-text search.

```bash
seek index              # Index all configured paths
seek search "query"     # Hybrid search
seek search "query" --mode exact   # FTS only
seek status             # Show index info
seek reindex            # Force full reindex
seek forget <path>      # Remove from index
```

### Configuration

Create `~/.config/seek/config.json` (or set `SEEK_CONFIG` env var):

```json
{
  "paths": [{"glob": "~/docs/**/*.md", "label": "docs"}],
  "sqliteSources": [{"path": "~/data.db", "tables": ["notes"], "label": "db"}],
  "model": "all-MiniLM-L6-v2",
  "dbPath": "~/.local/share/seek/seek.db",
  "chunkSize": 256,
  "chunkOverlap": 32
}
```

## pt — Project Tracker

Track and manage projects, tasks, and roadmap items in a local SQLite database.

```bash
pt list                    # List all tasks
pt --project openclaw list # List tasks for specific project
pt add "New task" --project openclaw --priority high --category dev
pt complete <task-id>      # Mark task as complete
```

## integrate — Unified Interface

Cross-reference and integrate data between different systems.

```bash
integrate cross-ref "query"     # Cross-reference between systems
integrate recommendations       # Get recommendations based on current state
integrate project-context       # Get context about projects
integrate status                # Show integration status
```

## backup — Backup Utility

Create and manage backups of Moltbot/OpenClaw systems.

```bash
backup create                 # Create a backup
backup list                   # List available backups
backup restore <backup-name>  # Restore from a backup
backup info                   # Show backup information
```

## gc — Google Calendar

Perform CRUD operations against Google Calendar.

```bash
gc list-calendars           # List all available calendars
gc list-events              # List events from a calendar (default: next 7 days)
gc create --summary "Title" --start "2026-02-01T10:00:00" --end "2026-02-01T11:00:00"  # Create new event
gc update <event_id> --summary "New Title"  # Update an existing event
gc delete <event_id>        # Delete an event
```

Note: Requires Google Calendar authentication setup with proper OAuth credentials.

## sync — Synchronization Tool

Synchronize and verify consistency between memory files and databases.

```bash
sync check                    # Check consistency between memory and database
sync sync                     # Sync memory files to database
sync export                   # Export database to memory file
```

Note: Real-time synchronization services have been deprecated in favor of database-as-source-of-truth model.

## service-manager — Process Management

Manage Moltbot/OpenClaw services and processes (deprecated for new installations).

```bash
service-manager status        # Show service status
service-manager list          # List registered processes
service-manager kill          # Kill specific process
```

Note: Process management functionality has been deprecated as no persistent services are needed in the new architecture.

## lookup — Documentation Lookup

Quickly look up documentation and information about the system.

```bash
lookup tools                  # Get information about tools
lookup commands               # Get information about commands
lookup <topic>                # Look up specific topic
```

## Docker Support

The project includes Docker support with externalizable data sources:

- `Dockerfile.quick` - Optimized Dockerfile with externalized data sources for persistence and security enhancements
- See `docker-readme.md` for detailed Docker usage instructions