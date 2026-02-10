# MoltBot Helpers

CLI tools for OpenClaw task management, family planning, and semantic search.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          WSL (Host)                             │
│  ┌─────────────────┐                                            │
│  │    OpenClaw     │  ← Runs here for direct system access      │
│  │    Gateway      │                                            │
│  └────────┬────────┘                                            │
│           │ port-forward (5433)                                 │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Kubernetes (openclaw-cluster)               │   │
│  │  ┌─────────────────────────────────────────────────┐    │   │
│  │  │              PostgreSQL (postgres-db)            │    │   │
│  │  │  ┌─────────────┬──────────────┬─────────────┐   │    │   │
│  │  │  │project_track│   fp_*       │  seek_*     │   │    │   │
│  │  │  │    (pt)     │   (fp)       │  (seek)     │   │    │   │
│  │  │  └─────────────┴──────────────┴─────────────┘   │    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

**All tools share a single PostgreSQL database** in the Kubernetes cluster.

## Quick Start

### 1. Port-forward PostgreSQL (run in WSL)
```bash
kubectl port-forward service/postgres-service 5433:5432 -n default
```

### 2. Initialize database
```bash
# From Docker
docker run --rm --add-host=host.docker.internal:host-gateway \
  -e PT_DB_HOST=host.docker.internal \
  moltbot-helpers-quick python3 scripts/init_db.py

# Or directly in WSL (with venv)
python3 scripts/init_db.py
```

### 3. Use the tools
```bash
# Project Tracker
pt --project openclaw list
pt --project openclaw add -c roadmap -t "New feature" -d "Description"

# Family Planner  
fp tasks
fp balances
fp add-task "Review documents" P1

# Semantic Search
seek init
seek index
seek search "kubernetes deployment"
```

## CLI Tools

### pt - Project Tracker
Manages tasks, roadmap items, bugs, and features across projects.

```bash
pt --project <name> list [--status new|in_progress|completed]
pt --project <name> add -c <category> -t <title> [-d description] [--priority high]
pt --project <name> update <id> --status completed
pt --project <name> search <query>
```

### fp - Family Planner
Personal/family information management.

```bash
fp init           # Initialize tables
fp tasks          # Show open tasks
fp balances       # Show financial balances
fp people         # List family members
fp docs [person]  # Show documents
fp search <term>  # Search everything
```

### seek - Semantic Search
Local semantic search across files and databases.

```bash
seek init         # Initialize tables
seek index        # Index configured paths
seek search <q>   # Search indexed content
seek status       # Show index status
```

## Database Connection

All tools use these environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `PT_DB_HOST` | `localhost` | PostgreSQL host |
| `PT_DB_PORT` | `5433` | PostgreSQL port |
| `PT_DB_NAME` | `financial_analysis` | Database name |
| `PT_DB_USER` | `finance_user` | Database user |
| `PT_DB_PASSWORD` | `secure_finance_password` | Database password |

## Docker Usage

Build and run:
```bash
cd /home/fred/projects/moltbot-helpers
docker build -t moltbot-helpers-quick:latest .

# Run any command
docker run --rm --add-host=host.docker.internal:host-gateway \
  -e PT_DB_HOST=host.docker.internal \
  moltbot-helpers-quick pt --project openclaw list
```

## Development

```bash
# Create venv
python3 -m venv .venv
source .venv/bin/activate

# Install in development mode
pip install -e .

# Now pt, fp, seek are available
pt --project test list
```

## Files

```
moltbot-helpers/
├── src/
│   ├── pt/cli.py          # Project tracker
│   ├── fp/cli.py          # Family planner
│   └── seek/              # Semantic search
├── scripts/
│   └── init_db.py         # Database initialization
├── k8s-openclaw-services.yaml  # K8s PostgreSQL deployment
├── Dockerfile
└── pyproject.toml
```
