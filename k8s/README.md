# Kubernetes Deployment for Daily Quote

This directory contains Kubernetes manifests and scripts for deploying the Daily Quote application to a Kubernetes cluster.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Kubernetes Cluster                                   │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    NGINX Ingress Controller                            │  │
│  │                    (ingress-nginx namespace)                           │  │
│  │                                                                        │  │
│  │    ┌─────────────────────────────────────────────────────────────┐    │  │
│  │    │              daily-quote.local (Port 80/443)                 │    │  │
│  │    └────────────────────────┬────────────────────────────────────┘    │  │
│  └─────────────────────────────┼─────────────────────────────────────────┘  │
│                                │                                             │
│  ┌─────────────────────────────┼─────────────────────────────────────────┐  │
│  │                    daily-quote namespace                               │  │
│  │                             │                                          │  │
│  │         ┌───────────────────┴───────────────────┐                     │  │
│  │         │                                       │                     │  │
│  │         ▼                                       ▼                     │  │
│  │  ┌─────────────────────┐          ┌─────────────────────┐            │  │
│  │  │   Frontend Service  │          │     API Service     │            │  │
│  │  │    (ClusterIP)      │          │    (ClusterIP)      │            │  │
│  │  │    Port: 80         │          │    Port: 80→8000    │            │  │
│  │  └──────────┬──────────┘          └──────────┬──────────┘            │  │
│  │             │                                │                        │  │
│  │             ▼                                ▼                        │  │
│  │  ┌─────────────────────┐          ┌─────────────────────┐            │  │
│  │  │ Frontend Deployment │          │   API Deployment    │            │  │
│  │  │  (nginx + React)    │          │    (FastAPI)        │            │  │
│  │  │  Replicas: 1        │          │   Replicas: 1       │            │  │
│  │  └─────────────────────┘          └──────────┬──────────┘            │  │
│  │                                              │                        │  │
│  │                                              ▼                        │  │
│  │                              ┌───────────────────────────┐           │  │
│  │                              │   Persistent Volumes      │           │  │
│  │                              │  ┌─────────┐ ┌─────────┐  │           │  │
│  │                              │  │api-data │ │ quotes  │  │           │  │
│  │                              │  │  (1Gi)  │ │ (500Mi) │  │           │  │
│  │                              │  └─────────┘ └─────────┘  │           │  │
│  │                              └───────────────────────────┘           │  │
│  │                                                                       │  │
│  │  ┌──────────────────────────────────────────────────────────────┐    │  │
│  │  │                    ConfigMaps & Secrets                       │    │  │
│  │  │  • daily-quote-config (env vars, settings)                   │    │  │
│  │  │  • daily-quote-secrets (API keys, passwords)                 │    │  │
│  │  └──────────────────────────────────────────────────────────────┘    │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                         kube-system namespace                          │  │
│  │   CoreDNS, kube-proxy, kube-scheduler, kube-controller-manager        │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  Nodes:                                                                      │
│  ┌─────────────────────────┐    ┌─────────────────────────┐                 │
│  │   Control Plane Node    │    │     Worker Node         │                 │
│  │   (control-plane)       │    │     (worker)            │                 │
│  └─────────────────────────┘    └─────────────────────────┘                 │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Files Overview

| File | Description |
|------|-------------|
| `kind-config.yaml` | kind cluster configuration with ingress support |
| `namespace.yaml` | Kubernetes namespace for the application |
| `configmap.yaml` | Application configuration (non-sensitive) |
| `secrets.yaml` | Sensitive configuration (passwords, keys) |
| `storage.yaml` | Persistent Volume Claims for data persistence |
| `api-deployment.yaml` | API deployment and service |
| `frontend-deployment.yaml` | Frontend deployment and service |
| `ingress.yaml` | Ingress configuration for routing |
| `deploy.sh` / `deploy.bat` | Deployment scripts |
| `cleanup.sh` / `cleanup.bat` | Cleanup scripts |

## Prerequisites

- **Docker Desktop** with Kubernetes enabled (kind or built-in)
- **kubectl** installed and configured
- **kind** CLI (optional - only needed if not using Docker Desktop's built-in cluster)

## Quick Start

### Option 1: Use Docker Desktop's Built-in Kubernetes (Recommended)

If you have Docker Desktop with Kubernetes/kind already enabled:

**Windows (PowerShell)**
```powershell
cd k8s
.\deploy.bat --build --use-desktop
```

**Linux/macOS**
```bash
cd k8s
./deploy.sh --build --use-desktop
```

### Option 2: Create a New Kind Cluster

If you want to create a separate kind cluster (requires kind CLI):

**Windows (PowerShell)**
```powershell
cd k8s
.\deploy.bat --build
```

**Linux/macOS**
```bash
cd k8s
./deploy.sh --build
```

### Option 3: Clean Deploy (Fresh Cluster)

Delete any existing cluster and create a new one:

```powershell
# Windows
.\deploy.bat --build --clean

# Linux/macOS
./deploy.sh --build --clean
```

## Script Options

| Option | Description |
|--------|-------------|
| `--build` | Build Docker images before deploying |
| `--clean` | Delete existing cluster and create a fresh one |
| `--use-desktop` | Use Docker Desktop's built-in Kubernetes cluster |

## Manual Deployment

If you prefer to deploy manually:

```bash
# 1. Ensure kubectl is pointing to your cluster
kubectl config current-context

# 2. Build Docker images
docker-compose -f ../docker-compose.v2.yml build

# 3. If using kind CLI (not Docker Desktop), load images:
kind load docker-image daily_quote-api:latest --name <cluster-name>
kind load docker-image daily_quote-frontend:latest --name <cluster-name>

# 4. Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# 5. Wait for ingress controller
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s

# 6. Deploy application
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secrets.yaml
kubectl apply -f storage.yaml
kubectl apply -f api-deployment.yaml
kubectl apply -f frontend-deployment.yaml
kubectl apply -f ingress.yaml
```

## Accessing the Application

1. **Add to hosts file** (as Administrator/root):

   **Windows** (`C:\Windows\System32\drivers\etc\hosts`):
   ```
   127.0.0.1 daily-quote.local
   ```

   **Linux/macOS** (`/etc/hosts`):
   ```
   127.0.0.1 daily-quote.local
   ```

2. **Access URLs**:
   - Frontend: http://daily-quote.local
   - API Docs: http://daily-quote.local/api/docs

3. **Default Credentials**:
   - Username: `admin`
   - Password: `admin123`

## Alternative Access (Port Forward)

If ingress is not working, use port-forward:

```bash
# Access API directly
kubectl port-forward -n daily-quote svc/daily-quote-api 8000:80

# Access Frontend directly
kubectl port-forward -n daily-quote svc/daily-quote-frontend 3000:80
```

Then access at:
- API: http://localhost:8000
- Frontend: http://localhost:3000

## Useful Commands

```bash
# View all resources in the namespace
kubectl get all -n daily-quote

# View pods
kubectl get pods -n daily-quote

# View pod logs
kubectl logs -n daily-quote -l component=api -f
kubectl logs -n daily-quote -l component=frontend -f

# Describe resources for debugging
kubectl describe deployment daily-quote-api -n daily-quote
kubectl describe pod -n daily-quote -l component=api

# Scale deployments
kubectl scale deployment daily-quote-api --replicas=2 -n daily-quote

# Get service details
kubectl get svc -n daily-quote

# Check ingress status
kubectl get ingress -n daily-quote
kubectl describe ingress daily-quote-ingress -n daily-quote

# View cluster nodes
kubectl get nodes

# View all namespaces
kubectl get namespaces
```

## Cleanup

### Remove Application Only

```bash
# Windows
.\cleanup.bat

# Linux/macOS
./cleanup.sh
```

### Remove Application and Cluster

```bash
# Windows
.\cleanup.bat --cluster

# Linux/macOS
./cleanup.sh --cluster
```

## Troubleshooting

### ErrImageNeverPull / ErrImagePull

This happens when images aren't available in the cluster. Solutions:

1. **Using Docker Desktop cluster** (`--use-desktop`): Images are automatically available
2. **Using kind CLI cluster**: Load images with:
   ```bash
   kind load docker-image daily_quote-api:latest --name <cluster-name>
   kind load docker-image daily_quote-frontend:latest --name <cluster-name>
   ```

### Ingress Controller Not Ready

Wait a few minutes and check status:
```bash
kubectl get pods -n ingress-nginx
kubectl describe pod -n ingress-nginx -l app.kubernetes.io/component=controller
```

### Webhook Errors When Applying Ingress

Wait for ingress controller to be fully ready, then retry:
```bash
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=300s

kubectl apply -f ingress.yaml
```

### Multiple Clusters Confusion

Check which cluster kubectl is connected to:
```bash
# List all contexts
kubectl config get-contexts

# See current context
kubectl config current-context

# Switch context
kubectl config use-context kind-daily-quote-cluster
kubectl config use-context kind-desktop
kubectl config use-context docker-desktop
```

### Checking Cluster Type

```bash
# List kind CLI clusters
kind get clusters

# Get nodes (shows cluster type in node names)
kubectl get nodes
```
