#!/bin/bash
# Deploy Daily Quote application to Kubernetes (kind)
# Usage: ./deploy.sh [--build] [--clean]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CLUSTER_NAME="daily-quote-cluster"

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
        *)
            echo "Unknown option: $1"
            echo "Usage: ./deploy.sh [--build] [--clean]"
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
    
    if ! command -v kind &> /dev/null; then
        log_error "kind is not installed. Please install kind: https://kind.sigs.k8s.io/docs/user/quick-start/#installation"
        exit 1
    fi
    
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed. Please install kubectl."
        exit 1
    fi
    
    log_info "All prerequisites met!"
}

# Create kind cluster
create_cluster() {
    if kind get clusters 2>/dev/null | grep -q "$CLUSTER_NAME"; then
        log_info "Cluster '$CLUSTER_NAME' already exists"
        
        if [ "$CLEAN_DEPLOY" = true ]; then
            log_warn "Deleting existing cluster for clean deploy..."
            kind delete cluster --name "$CLUSTER_NAME"
            log_info "Creating new cluster..."
            kind create cluster --config "$SCRIPT_DIR/kind-config.yaml"
        fi
    else
        log_info "Creating kind cluster '$CLUSTER_NAME'..."
        kind create cluster --config "$SCRIPT_DIR/kind-config.yaml"
    fi
    
    # Set kubectl context
    kubectl cluster-info --context "kind-$CLUSTER_NAME"
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
    log_info "Loading images into kind cluster..."
    
    kind load docker-image daily_quote-api:latest --name "$CLUSTER_NAME"
    kind load docker-image daily_quote-frontend:latest --name "$CLUSTER_NAME"
    
    log_info "Images loaded successfully!"
}

# Install NGINX Ingress Controller
install_ingress() {
    log_info "Installing NGINX Ingress Controller..."
    
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
    
    log_info "Waiting for ingress controller to be ready..."
    kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=120s
    
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
    kubectl apply -f "$SCRIPT_DIR/ingress.yaml"
    
    log_info "Waiting for deployments to be ready..."
    kubectl wait --namespace daily-quote \
        --for=condition=available deployment \
        --all \
        --timeout=120s
    
    log_info "Application deployed successfully!"
}

# Print access information
print_access_info() {
    echo ""
    echo "=============================================="
    echo -e "${GREEN}Daily Quote Application Deployed!${NC}"
    echo "=============================================="
    echo ""
    echo "Add the following line to your hosts file:"
    echo "  Windows: C:\\Windows\\System32\\drivers\\etc\\hosts"
    echo "  Linux/Mac: /etc/hosts"
    echo ""
    echo "  127.0.0.1 daily-quote.local"
    echo ""
    echo "Access the application at:"
    echo "  http://daily-quote.local"
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
    echo "  kubectl logs -n daily-quote -l component=api"
    echo "  kubectl logs -n daily-quote -l component=frontend"
    echo "=============================================="
}

# Main execution
main() {
    check_prerequisites
    create_cluster
    
    if [ "$BUILD_IMAGES" = true ]; then
        build_images
    fi
    
    load_images
    install_ingress
    deploy_app
    print_access_info
}

main
