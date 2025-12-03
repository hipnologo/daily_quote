# Kubernetes Deployment for Daily Quote

This directory contains Kubernetes manifests and scripts for deploying the Daily Quote application to a Kubernetes cluster.

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

## Quick Start

### Windows (PowerShell)

```powershell
# From the k8s directory
.\deploy.bat --build
```

### Linux/macOS

```bash
# From the k8s directory
./deploy.sh --build
```

## Manual Deployment

If you prefer to deploy manually:

```bash
# 1. Create kind cluster
kind create cluster --config kind-config.yaml

# 2. Build and load images
docker-compose -f ../docker-compose.v2.yml build
kind load docker-image daily_quote-api:latest --name daily-quote-cluster
kind load docker-image daily_quote-frontend:latest --name daily-quote-cluster

# 3. Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# 4. Wait for ingress controller
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s

# 5. Deploy application
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secrets.yaml
kubectl apply -f storage.yaml
kubectl apply -f api-deployment.yaml
kubectl apply -f frontend-deployment.yaml
kubectl apply -f ingress.yaml
```

## Accessing the Application

1. Add the following entry to your hosts file:
   - **Windows**: `C:\Windows\System32\drivers\etc\hosts`
   - **Linux/macOS**: `/etc/hosts`

   ```
   127.0.0.1 daily-quote.local
   ```

2. Access the application:
   - Frontend: http://daily-quote.local
   - API Docs: http://daily-quote.local/api/docs

## Useful Commands

```bash
# View pods
kubectl get pods -n daily-quote

# View logs
kubectl logs -n daily-quote -l component=api
kubectl logs -n daily-quote -l component=frontend

# Describe resources
kubectl describe deployment daily-quote-api -n daily-quote

# Port forward for debugging
kubectl port-forward -n daily-quote svc/daily-quote-api 8000:8000

# Scale deployments
kubectl scale deployment daily-quote-api --replicas=2 -n daily-quote
```

## Cleanup

```bash
# Remove application only
./cleanup.sh          # Linux/macOS
cleanup.bat           # Windows

# Remove application and cluster
./cleanup.sh --cluster    # Linux/macOS
cleanup.bat --cluster     # Windows
```
