#!/bin/bash

echo "=== Kubernetes Diagnostic ==="
echo

echo "1. Checking if k3s is installed..."
if command -v k3s &> /dev/null; then
    echo "✓ k3s is installed"
    k3s --version
else
    echo "❌ k3s is not installed in PATH"
fi

echo
echo "2. Checking if kubectl is available..."
if command -v kubectl &> /dev/null; then
    echo "✓ kubectl is available"
    kubectl version --client
else
    echo "❌ kubectl is not available"
fi

echo
echo "3. Checking for k3s service status..."
if systemctl is-active --quiet k3s 2>/dev/null; then
    echo "✓ k3s service is active"
else
    echo "ℹ k3s service is not active"
    # Check if k3s command exists but service isn't running
    if command -v k3s &> /dev/null; then
        echo "  Note: k3s is installed but the service may not be running"
        echo "  You may need to start it with: sudo k3s server --write-kubeconfig-mode 644 &"
    fi
fi

echo
echo "4. Checking for kubeconfig..."
if [ -f "$HOME/.kube/config" ]; then
    echo "✓ Found kubeconfig at ~/.kube/config"
elif [ -f "/etc/rancher/k3s/k3s.yaml" ]; then
    echo "✓ Found k3s config at /etc/rancher/k3s/k3s.yaml"
else
    echo "ℹ No kubeconfig found - this explains why kubectl hangs"
fi

echo
echo "=== Diagnostic Complete ==="