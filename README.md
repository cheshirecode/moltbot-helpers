# moltbot-helpers

Two CLI tools for Moltbot: `fp` (family planner) and `seek` (local semantic search).

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
