# moltbot-helpers

CLI tools for Moltbot/OpenClaw systems: `fp` (family planner), `seek` (local semantic search), `pt` (project tracker), `integrate` (unified interface), `backup` (backup utility), `sync` (synchronization), and `service-manager` (process management).

## Install

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

## sync — Synchronization Service

Synchronize data between different systems and sources.

```bash
sync status                   # Show synchronization status
sync run                      # Run synchronization
sync watch                    # Watch for changes and sync automatically
```

## service-manager — Process Management

Manage Moltbot/OpenClaw services and processes.

```bash
service-manager status        # Show service status
service-manager start         # Start services
service-manager stop          # Stop services
service-manager restart       # Restart services
```

## lookup — Documentation Lookup

Quickly look up documentation and information about the system.

```bash
lookup tools                  # Get information about tools
lookup commands               # Get information about commands
lookup <topic>                # Look up specific topic
```

## Docker Support

The project includes Docker support with externalizable data sources:

- `Dockerfile` - Standard Dockerfile that creates empty databases
- `Dockerfile.quick` - Optimized Dockerfile with externalized data sources for persistence
- See `docker-readme.md` for detailed Docker usage instructions