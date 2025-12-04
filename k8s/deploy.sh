#!/bin/bash
# Deploy Daily Quote application to Kubernetes
# Usage: ./deploy.sh [--build] [--clean] [--use-desktop]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CLUSTER_NAME="daily-quote-cluster"
USE_KIND_CLI=true

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Parse arguments
BUILD_IMAGES=false
CLEAN_DEPLOY=false
USE_DOCKER_DESKTOP=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --build)
            BUILD_IMAGES=true
            shift
            ;;
        --clean)
            CLEAN_DEPLOY=true
            shift
            ;;
        --use-desktop)
            USE_DOCKER_DESKTOP=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: ./deploy.sh [--build] [--clean] [--use-desktop]"
            echo ""
            echo "Options:"
            echo "  --build        Build Docker images before deploying"
            echo "  --clean        Delete existing cluster and create fresh one"
            echo "  --use-desktop  Use Docker Desktop's built-in Kubernetes cluster"
            exit 1
            ;;
    esac
done

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker Desktop."
        exit 1
    fi
    
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed. Please install kubectl."
        exit 1
    fi
    
    log_info "All prerequisites met!"
}

# Setup cluster
setup_cluster() {
    log_info "Checking for existing Kubernetes clusters..."
    
    # Check for Docker Desktop kind cluster (kind-desktop context)
    if kubectl config get-contexts 2>/dev/null | grep -q "kind-desktop"; then
        log_info "Found Docker Desktop kind cluster 'kind-desktop'"
        if [ "$USE_DOCKER_DESKTOP" = true ]; then
            log_info "Using Docker Desktop's kind cluster as requested..."
            CLUSTER_NAME="desktop"
            USE_KIND_CLI=false
            kubectl config use-context kind-desktop
            return
        else
            log_info "Docker Desktop kind cluster available. Use --use-desktop to use it."
        fi
    fi
    
    # Check for docker-desktop context (standard Docker Desktop Kubernetes)
    if kubectl config get-contexts 2>/dev/null | grep -q "docker-desktop"; then
        log_info "Found Docker Desktop Kubernetes cluster"
        if [ "$USE_DOCKER_DESKTOP" = true ]; then
            log_info "Using Docker Desktop's Kubernetes cluster as requested..."
            CLUSTER_NAME="docker-desktop"
            USE_KIND_CLI=false
            kubectl config use-context docker-desktop
            return
        else
            log_info "Docker Desktop Kubernetes available. Use --use-desktop to use it."
        fi
    fi
    
    # Check if kind CLI is available
    if ! command -v kind &> /dev/null; then
        log_warn "kind CLI not found. Checking for existing Kubernetes cluster..."
        if kubectl cluster-info &> /dev/null; then
            log_info "Using existing Kubernetes cluster from current context"
            USE_KIND_CLI=false
            return
        else
            log_error "No Kubernetes cluster available and kind CLI not installed."
            log_error "Either enable Kubernetes in Docker Desktop or install kind."
            exit 1
        fi
    fi
    
    # Check if our specific cluster exists via kind CLI
    if kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
        log_info "Found existing kind cluster '$CLUSTER_NAME'"
        if [ "$CLEAN_DEPLOY" = true ]; then
            log_warn "Deleting existing cluster for clean deploy..."
            kind delete cluster --name "$CLUSTER_NAME"
            log_info "Creating new cluster '$CLUSTER_NAME'..."
            kind create cluster --config "$SCRIPT_DIR/kind-config.yaml"
        else
            log_info "Using existing cluster '$CLUSTER_NAME'"
        fi
        kubectl config use-context "kind-$CLUSTER_NAME"
        return
    fi
    
    # Check for any existing kind clusters
    EXISTING_CLUSTER=$(kind get clusters 2>/dev/null | head -n 1)
    if [ -n "$EXISTING_CLUSTER" ]; then
        log_info "Found existing kind cluster: $EXISTING_CLUSTER"
        if [ "$CLEAN_DEPLOY" = true ]; then
            log_info "--clean specified, creating new cluster..."
            kind create cluster --config "$SCRIPT_DIR/kind-config.yaml"
            kubectl config use-context "kind-$CLUSTER_NAME"
        else
            log_info "Using existing cluster '$EXISTING_CLUSTER'"
            CLUSTER_NAME="$EXISTING_CLUSTER"
            kubectl config use-context "kind-$EXISTING_CLUSTER"
        fi
        return
    fi
    
    log_info "Creating new kind cluster '$CLUSTER_NAME'..."
    kind create cluster --config "$SCRIPT_DIR/kind-config.yaml"
    kubectl config use-context "kind-$CLUSTER_NAME"
}

# Verify cluster connection
verify_cluster() {
    log_info "Verifying cluster connection..."
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    kubectl cluster-info
}

# Build Docker images
build_images() {
    log_info "Building Docker images..."
    cd "$PROJECT_ROOT"
    docker-compose -f docker-compose.v2.yml build
    log_info "Docker images built successfully!"
}

# Load images into kind cluster
load_images() {
    if [ "$USE_KIND_CLI" = true ]; then
        log_info "Loading images into kind cluster '$CLUSTER_NAME'..."
        kind load docker-image daily_quote-api:latest --name "$CLUSTER_NAME"
        kind load docker-image daily_quote-frontend:latest --name "$CLUSTER_NAME"
        log_info "Images loaded successfully!"
    else
        log_info "Using Docker Desktop cluster - images are automatically available"
    fi
}

# Install NGINX Ingress Controller
install_ingress() {
    log_info "Checking NGINX Ingress Controller..."
    
    if kubectl get namespace ingress-nginx &> /dev/null; then
        log_info "NGINX Ingress Controller already installed"
        return
    fi
    
    log_info "Installing NGINX Ingress Controller..."
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
    
    log_info "Waiting for ingress controller to be ready (this may take a few minutes)..."
    kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=300s || log_warn "Ingress controller not ready yet, continuing..."
    
    log_info "Ingress controller installed!"
}

# Deploy application
deploy_app() {
    log_info "Deploying Daily Quote application..."
    
    # Apply manifests in order
    kubectl apply -f "$SCRIPT_DIR/namespace.yaml"
    kubectl apply -f "$SCRIPT_DIR/configmap.yaml"
    kubectl apply -f "$SCRIPT_DIR/secrets.yaml"
    kubectl apply -f "$SCRIPT_DIR/storage.yaml"
    kubectl apply -f "$SCRIPT_DIR/api-deployment.yaml"
    kubectl apply -f "$SCRIPT_DIR/frontend-deployment.yaml"
    
    # Try to apply ingress with retry
    kubectl apply -f "$SCRIPT_DIR/ingress.yaml" 2>/dev/null || {
        log_warn "Ingress creation failed. Retrying in 10 seconds..."
        sleep 10
        kubectl apply -f "$SCRIPT_DIR/ingress.yaml"
    }
    
    log_info "Waiting for deployments to be ready..."
    kubectl wait --namespace daily-quote \
        --for=condition=available deployment \
        --all \
        --timeout=300s || log_warn "Some deployments may not be ready"
    
    log_info "Application deployed!"
}

# Print access information
print_access_info() {
    echo ""
    echo "=============================================="
    echo -e "${GREEN}Daily Quote Application Deployed!${NC}"
    echo "=============================================="
    echo ""
    echo "Current cluster context:"
    kubectl config current-context
    echo ""
    echo "Pod status:"
    kubectl get pods -n daily-quote
    echo ""
    echo "Add the following line to your hosts file:"
    echo "  Windows: C:\\Windows\\System32\\drivers\\etc\\hosts"
    echo "  Linux/Mac: /etc/hosts"
    echo ""
    echo "  127.0.0.1 daily-quote.local"
    echo ""
    echo "Access the application at:"
    echo "  http://daily-quote.local"
    echo "  or http://localhost (if using port-forward)"
    echo ""
    echo "API Documentation:"
    echo "  http://daily-quote.local/api/docs"
    echo ""
    echo "Default credentials:"
    echo "  Username: admin"
    echo "  Password: admin123"
    echo ""
    echo "Useful commands:"
    echo "  kubectl get pods -n daily-quote"
    echo "  kubectl get svc -n daily-quote"
    echo "  kubectl logs -n daily-quote -l component=api"
    echo "  kubectl logs -n daily-quote -l component=frontend"
    echo "  kubectl port-forward -n daily-quote svc/daily-quote-api 8000:80"
    echo "=============================================="
}

# Main execution
main() {
    check_prerequisites
    setup_cluster
    verify_cluster
    
    if [ "$BUILD_IMAGES" = true ]; then
        build_images
    fi
    
    load_images
    install_ingress
    deploy_app
    print_access_info
}

main
