# OpenClaw Task Management Architecture

## Overview

OpenClaw runs in WSL for direct system access, while data persists in a PostgreSQL database running in the Kubernetes cluster.

## System Layout

```
┌────────────────────────────────────────────────────────────────────────────┐
│                              WSL Environment                                │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         OpenClaw Gateway                              │  │
│  │                                                                       │  │
│  │  • Manages conversations                                              │  │
│  │  • Executes shell commands                                            │  │
│  │  • Direct filesystem access                                           │  │
│  │  • Runs cron jobs / heartbeats                                        │  │
│  └───────────────────────────┬──────────────────────────────────────────┘  │
│                              │                                             │
│  ┌───────────────────────────▼──────────────────────────────────────────┐  │
│  │                        Docker (one-off)                               │  │
│  │                                                                       │  │
│  │  docker run --rm --add-host=host.docker.internal:host-gateway \       │  │
│  │    -e PT_DB_HOST=host.docker.internal \                               │  │
│  │    moltbot-helpers-quick:latest pt --project openclaw list            │  │
│  │                                                                       │  │
│  └───────────────────────────┬──────────────────────────────────────────┘  │
│                              │                                             │
│  ┌───────────────────────────▼──────────────────────────────────────────┐  │
│  │                    kubectl port-forward                               │  │
│  │                                                                       │  │
│  │  kubectl port-forward service/postgres-service 5433:5432 -n default   │  │
│  │  (runs as background process)                                         │  │
│  └───────────────────────────┬──────────────────────────────────────────┘  │
│                              │                                             │
└──────────────────────────────┼─────────────────────────────────────────────┘
                               │
┌──────────────────────────────▼─────────────────────────────────────────────┐
│                         Kubernetes (openclaw-cluster)                       │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      PostgreSQL (postgres-service)                    │  │
│  │                                                                       │  │
│  │  Database: financial_analysis                                         │  │
│  │  User: finance_user                                                   │  │
│  │                                                                       │  │
│  │  Tables:                                                              │  │
│  │  ├── project_tracker  (pt tool)                                       │  │
│  │  ├── fp_*             (fp tool - family planner)                      │  │
│  │  └── seek_*           (seek tool - semantic search)                   │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

1. **OpenClaw** receives a request (e.g., "add a task to the roadmap")
2. **OpenClaw** runs a Docker container with `moltbot-helpers-quick`
3. **Docker** connects to `host.docker.internal:5433` 
4. **Port-forward** routes traffic to PostgreSQL in the K8s cluster
5. **PostgreSQL** stores/retrieves data
6. Result flows back to OpenClaw

## Running Tools

### From OpenClaw (via Docker)

```bash
# List project tasks
docker run --rm --add-host=host.docker.internal:host-gateway \
  -e PT_DB_HOST=host.docker.internal \
  moltbot-helpers-quick:latest pt --project openclaw list

# Add a task
docker run --rm --add-host=host.docker.internal:host-gateway \
  -e PT_DB_HOST=host.docker.internal \
  moltbot-helpers-quick:latest pt --project openclaw add \
    -c roadmap -t "New feature" --priority high

# Family planner
docker run --rm --add-host=host.docker.internal:host-gateway \
  -e PT_DB_HOST=host.docker.internal \
  moltbot-helpers-quick:latest fp tasks
```

### Directly from WSL (with port-forward active)

```bash
# Ensure port-forward is running
kubectl port-forward service/postgres-service 5433:5432 -n default &

# Install locally
cd ~/projects/moltbot-helpers
pip install -e .

# Use directly
pt --project openclaw list
fp tasks
seek search "kubernetes"
```

## Startup Sequence

1. Start the K8s cluster if not running:
   ```bash
   k3d cluster list
   k3d cluster start openclaw-cluster
   ```

2. Start port-forward (keep running in background):
   ```bash
   kubectl port-forward service/postgres-service 5433:5432 -n default &
   ```

3. OpenClaw is now ready to use tools

## Database Initialization

Run once after cluster creation:

```bash
docker run --rm --add-host=host.docker.internal:host-gateway \
  -e PT_DB_HOST=host.docker.internal \
  moltbot-helpers-quick:latest python3 scripts/init_db.py
```

## Why This Architecture?

| Component | Location | Reason |
|-----------|----------|--------|
| OpenClaw Gateway | WSL | Direct access to filesystem, shell, system |
| PostgreSQL | K8s cluster | Persistent, isolated, scalable |
| CLI Tools | Docker | Consistent environment, no local deps |

## Troubleshooting

### Port-forward died?
```bash
# Check if running
pgrep -f "port-forward.*postgres"

# Restart
kubectl port-forward service/postgres-service 5433:5432 -n default &
```

### Can't connect to database?
```bash
# Test connection
docker run --rm --add-host=host.docker.internal:host-gateway \
  -e PT_DB_HOST=host.docker.internal \
  moltbot-helpers-quick:latest python3 -c \
  "import psycopg2; psycopg2.connect(host='host.docker.internal', port=5433, database='financial_analysis', user='finance_user', password='secure_finance_password'); print('OK')"
```

### Cluster not running?
```bash
k3d cluster list
k3d cluster start openclaw-cluster
```
