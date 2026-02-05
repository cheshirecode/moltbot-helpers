# Setting up k3s for OpenClaw Services

This document explains how to set up k3s (Kubernetes) to work with the OpenClaw services alongside WSL-based OpenClaw.

## Prerequisites

- WSL-based OpenClaw services running (these will continue to run in WSL for your direct management)
- Docker must be available

## Installing k3s

k3s is a lightweight Kubernetes distribution that's perfect for development and production.

### Installation Steps:

1. Install k3s as a service:
   ```bash
   curl -sfL https://get.k3s.io | sh -
   ```

2. Or install k3s with specific options for easier access:
   ```bash
   curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644
   ```

3. The above command will:
   - Install k3s as a systemd service
   - Configure k3s to run on boot
   - Set proper permissions on the kubeconfig file

4. Verify k3s is running:
   ```bash
   sudo k3s kubectl get nodes
   ```

## Configuring kubectl Access

To use kubectl from your regular user account (without sudo):

1. Create the kubeconfig directory:
   ```bash
   mkdir -p ~/.kube
   ```

2. Copy the k3s kubeconfig to your user directory:
   ```bash
   sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
   ```

3. Change ownership of the config file:
   ```bash
   sudo chown $USER:$USER ~/.kube/config
   ```

4. Test kubectl access:
   ```bash
   kubectl get nodes
   ```

## Setting Up OpenClaw Services in Kubernetes

Once k3s is running and kubectl is configured, you can set up the OpenClaw services:

```bash
cd /home/fred/projects/moltbot-helpers
./setup-k8s-services.sh
```

## Architecture

- **WSL**: OpenClaw gateway services run here for your direct management
- **Kubernetes (k3s)**: Supporting services like PostgreSQL run here
- **Communication**: WSL-based OpenClaw services connect to Kubernetes services using internal DNS

## Connecting WSL OpenClaw to Kubernetes PostgreSQL

When your WSL-based OpenClaw services need to connect to the PostgreSQL running in Kubernetes:

- Host: `postgres-db.openclaw-services.svc.cluster.local`
- Port: `5432`
- Database: `financial_analysis`
- User: `finance_user`
- Password: `secure_finance_password`

## Verification

After setup, verify everything is working:

1. Check that Kubernetes services are running:
   ```bash
   kubectl get pods -n openclaw-services
   ```

2. Check that your WSL OpenClaw services can connect to the PostgreSQL database.

## Troubleshooting

If you encounter issues:

1. Check if k3s service is running:
   ```bash
   sudo systemctl status k3s
   ```

2. If it's not running, start it:
   ```bash
   sudo systemctl start k3s
   ```

3. Check k3s logs:
   ```bash
   sudo journalctl -u k3s -f
   ```