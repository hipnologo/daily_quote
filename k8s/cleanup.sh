#!/bin/bash
# Clean up Daily Quote Kubernetes deployment
# Usage: ./cleanup.sh [--cluster]

set -e

CLUSTER_NAME="daily-quote-cluster"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

DELETE_CLUSTER=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --cluster)
            DELETE_CLUSTER=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: ./cleanup.sh [--cluster]"
            exit 1
            ;;
    esac
done

log_info "Deleting Daily Quote application resources..."

# Delete application resources
kubectl delete -f ingress.yaml --ignore-not-found=true 2>/dev/null || true
kubectl delete -f frontend-deployment.yaml --ignore-not-found=true 2>/dev/null || true
kubectl delete -f api-deployment.yaml --ignore-not-found=true 2>/dev/null || true
kubectl delete -f storage.yaml --ignore-not-found=true 2>/dev/null || true
kubectl delete -f secrets.yaml --ignore-not-found=true 2>/dev/null || true
kubectl delete -f configmap.yaml --ignore-not-found=true 2>/dev/null || true
kubectl delete -f namespace.yaml --ignore-not-found=true 2>/dev/null || true

log_info "Application resources deleted!"

if [ "$DELETE_CLUSTER" = true ]; then
    log_warn "Deleting kind cluster '$CLUSTER_NAME'..."
    kind delete cluster --name "$CLUSTER_NAME"
    log_info "Cluster deleted!"
fi

log_info "Cleanup complete!"
