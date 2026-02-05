#!/bin/bash

echo "=== OpenClaw K8s Services Setup ==="
echo "This script sets up Kubernetes services to work alongside WSL-based OpenClaw"
echo

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed or not in PATH"
    echo "Please install kubectl and ensure it's in your PATH"
    exit 1
fi

# Check if we have a kubernetes cluster available
if ! timeout 10 kubectl cluster-info &> /dev/null; then
    echo "❌ No Kubernetes cluster is currently accessible"
    echo
    echo "To set up k3s, please run the following commands as root:"
    echo
    echo "  # Install k3s"
    echo "  curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644"
    echo
    echo "  # Or if you want to start k3s server manually:"
    echo "  sudo k3s server --write-kubeconfig-mode 644 &"
    echo
    echo "  # Then copy the kubeconfig to your user directory:"
    echo "  mkdir -p ~/.kube"
    echo "  sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config"
    echo "  sudo chown \$USER:\$USER ~/.kube/config"
    echo
    echo "After setting up k3s, please run this script again."
    exit 1
fi

echo "✅ Kubernetes cluster is accessible"
echo

echo "Setting up OpenClaw services in Kubernetes..."
kubectl apply -f k8s-openclaw-services.yaml

echo
echo "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres-db -n openclaw-services --timeout=120s

echo
echo "=== K8s Services Setup Complete ==="
echo "PostgreSQL is now running in Kubernetes"
echo "WSL-based OpenClaw services can connect to it using:"
echo "  Host: postgres-db.openclaw-services.svc.cluster.local"
echo "  Port: 5432"
echo "  Database: financial_analysis"
echo "  User: finance_user"
echo "  Password: secure_finance_password"
echo
echo "Services:"
kubectl get svc -n openclaw-services
echo
echo "Deployments:"
kubectl get deployments -n openclaw-services
echo
echo "Note: OpenClaw gateway services continue to run in WSL for your direct management"