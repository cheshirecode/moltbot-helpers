# Moltbot Helpers - OpenClaw Integration

This repository contains helper tools for the OpenClaw ecosystem, including project tracking (pt), family planning (fp), semantic search (seek), and more.

## Infrastructure Setup

This repository now contains the Docker and Kubernetes configurations for OpenClaw services, keeping the main OpenClaw repository clean.

### Docker Compose

The `docker-compose.yml` file defines services that can be run locally using Docker Compose.

### Kubernetes Services

The `k8s-openclaw-services.yaml` file defines services that can be run in Kubernetes, designed to work alongside WSL-based OpenClaw services.

## Setup Options

### Option 1: Docker Compose (Existing)
Use the existing docker-compose file for local development:
```bash
docker-compose up -d
```

### Option 2: Kubernetes Services (New)
Use the Kubernetes configuration to run supporting services (like PostgreSQL) in a cluster while keeping OpenClaw gateway in WSL:

1. Ensure you have a Kubernetes cluster running (minikube, kind, k3s, etc.)
2. Run the setup script:
```bash
./setup-k8s-services.sh
```

This setup allows you to:
- Keep OpenClaw gateway services running in WSL for direct management
- Run supporting services (like PostgreSQL) in Kubernetes
- Maintain separation of concerns while enabling integration

## Configuration

When running OpenClaw in WSL with services in Kubernetes:
- PostgreSQL host: `postgres-db.openclaw-services.svc.cluster.local`
- PostgreSQL port: `5432`
- Database: `financial_analysis`
- Username: `finance_user`
- Password: `secure_finance_password`

## Clean Architecture

This approach keeps the main OpenClaw repository clean while providing flexible deployment options through moltbot-helpers.