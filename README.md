# Moltbot Helpers

Helper tools for the OpenClaw ecosystem, including project tracking (pt), family planning (fp), semantic search (seek), and more.

## Infrastructure

This repository contains Kubernetes configuration for OpenClaw services that work alongside WSL-based OpenClaw services.

### Kubernetes Services

The `k8s-openclaw-services.yaml` file defines services that can be run in Kubernetes, designed to work alongside WSL-based OpenClaw services.

### k3s Setup

To use the Kubernetes functionality, you need to set up k3s (lightweight Kubernetes). See `K3S_SETUP_INSTRUCTIONS.md` for detailed instructions.

#### Setup

To deploy the services to Kubernetes:

1. Set up k3s following the instructions in `K3S_SETUP_INSTRUCTIONS.md`
2. Run the setup script:
```bash
./setup-k8s-services.sh
```

This will set up PostgreSQL in Kubernetes for use with WSL-based OpenClaw services.

#### Architecture

- PostgreSQL database runs in Kubernetes
- OpenClaw gateway services run in WSL (for direct management)
- Services communicate across environments using Kubernetes networking