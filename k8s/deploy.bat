@echo off
REM Deploy Daily Quote application to Kubernetes - Windows version
REM Usage: deploy.bat [--build] [--clean] [--use-desktop]

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
set "CLUSTER_NAME=daily-quote-cluster"
set "USE_DOCKER_DESKTOP=false"
set "USE_KIND_CLI=true"

REM Parse arguments
set "BUILD_IMAGES=false"
set "CLEAN_DEPLOY=false"

:parse_args
if "%~1"=="" goto :end_parse
if "%~1"=="--build" (
    set "BUILD_IMAGES=true"
    shift
    goto :parse_args
)
if "%~1"=="--clean" (
    set "CLEAN_DEPLOY=true"
    shift
    goto :parse_args
)
if "%~1"=="--use-desktop" (
    set "USE_DOCKER_DESKTOP=true"
    shift
    goto :parse_args
)
echo Unknown option: %~1
echo Usage: deploy.bat [--build] [--clean] [--use-desktop]
echo.
echo Options:
echo   --build        Build Docker images before deploying
echo   --clean        Delete existing cluster and create fresh one
echo   --use-desktop  Use Docker Desktop's built-in Kubernetes cluster
exit /b 1

:end_parse

REM Check prerequisites
echo [INFO] Checking prerequisites...

where docker >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop.
    exit /b 1
)

where kubectl >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] kubectl is not installed. Please install kubectl.
    exit /b 1
)

echo [INFO] All prerequisites met!

REM Check for existing Kubernetes clusters
echo [INFO] Checking for existing Kubernetes clusters...

REM Check for Docker Desktop kind cluster (kind-desktop context)
kubectl config get-contexts 2>nul | findstr /C:"kind-desktop" >nul
if %ERRORLEVEL% equ 0 (
    echo [INFO] Found Docker Desktop kind cluster 'kind-desktop'
    if "%USE_DOCKER_DESKTOP%"=="true" (
        echo [INFO] Using Docker Desktop's kind cluster as requested...
        set "CLUSTER_NAME=desktop"
        set "USE_KIND_CLI=false"
        kubectl config use-context kind-desktop
        goto :skip_cluster_creation
    ) else (
        echo [INFO] Docker Desktop kind cluster available. Use --use-desktop to use it.
    )
)

REM Check for docker-desktop context (standard Docker Desktop Kubernetes)
kubectl config get-contexts 2>nul | findstr /C:"docker-desktop" >nul
if %ERRORLEVEL% equ 0 (
    echo [INFO] Found Docker Desktop Kubernetes cluster
    if "%USE_DOCKER_DESKTOP%"=="true" (
        echo [INFO] Using Docker Desktop's Kubernetes cluster as requested...
        set "CLUSTER_NAME=docker-desktop"
        set "USE_KIND_CLI=false"
        kubectl config use-context docker-desktop
        goto :skip_cluster_creation
    ) else (
        echo [INFO] Docker Desktop Kubernetes available. Use --use-desktop to use it.
    )
)

REM Check if kind CLI is available
where kind >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [WARN] kind CLI not found. Checking for existing Kubernetes cluster...
    kubectl cluster-info >nul 2>nul
    if %ERRORLEVEL% equ 0 (
        echo [INFO] Using existing Kubernetes cluster from current context
        set "USE_KIND_CLI=false"
        goto :skip_cluster_creation
    ) else (
        echo [ERROR] No Kubernetes cluster available and kind CLI not installed.
        echo [ERROR] Either enable Kubernetes in Docker Desktop or install kind.
        exit /b 1
    )
)

REM Check if our specific cluster exists via kind CLI
kind get clusters 2>nul | findstr /C:"%CLUSTER_NAME%" >nul
if %ERRORLEVEL% equ 0 (
    echo [INFO] Found existing kind cluster '%CLUSTER_NAME%'
    if "%CLEAN_DEPLOY%"=="true" (
        echo [WARN] Deleting existing cluster for clean deploy...
        kind delete cluster --name %CLUSTER_NAME%
        echo [INFO] Creating new cluster '%CLUSTER_NAME%'...
        kind create cluster --config "%SCRIPT_DIR%kind-config.yaml"
    ) else (
        echo [INFO] Using existing cluster '%CLUSTER_NAME%'
    )
    kubectl config use-context kind-%CLUSTER_NAME%
    goto :skip_cluster_creation
)

REM Check if any other kind clusters exist
for /f %%i in ('kind get clusters 2^>nul') do (
    echo [INFO] Found existing kind cluster: %%i
    if "%CLEAN_DEPLOY%"=="true" (
        echo [INFO] --clean specified, creating new cluster instead
        goto :create_new_cluster
    )
    echo [INFO] Using existing cluster '%%i'
    set "CLUSTER_NAME=%%i"
    kubectl config use-context kind-%%i
    goto :skip_cluster_creation
)

:create_new_cluster
echo [INFO] Creating new kind cluster '%CLUSTER_NAME%'...
kind create cluster --config "%SCRIPT_DIR%kind-config.yaml"
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to create kind cluster
    exit /b 1
)
kubectl config use-context kind-%CLUSTER_NAME%

:skip_cluster_creation
REM Verify cluster is accessible
echo [INFO] Verifying cluster connection...
kubectl cluster-info >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Cannot connect to Kubernetes cluster
    exit /b 1
)
kubectl cluster-info

REM Build Docker images if requested
if "%BUILD_IMAGES%"=="true" (
    echo [INFO] Building Docker images...
    pushd "%PROJECT_ROOT%"
    
    REM Build API image
    echo [INFO] Building API image...
    docker build -t daily-quote-api:latest -f admin-dashboard/api/Dockerfile admin-dashboard/api
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to build API image
        popd
        exit /b 1
    )
    
    REM Build combined frontend image (public + admin dashboard)
    echo [INFO] Building combined frontend image...
    docker build -t daily-quote-frontend:latest -f Dockerfile.frontend .
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to build frontend image
        popd
        exit /b 1
    )
    
    popd
    echo [INFO] Docker images built successfully!
)

REM Load images into cluster (only for kind CLI-managed clusters)
if "%USE_KIND_CLI%"=="true" (
    echo [INFO] Loading images into kind cluster '%CLUSTER_NAME%'...
    kind load docker-image daily-quote-api:latest --name %CLUSTER_NAME%
    kind load docker-image daily-quote-frontend:latest --name %CLUSTER_NAME%
    echo [INFO] Images loaded successfully!
) else (
    echo [INFO] Using Docker Desktop cluster - images are automatically available
)

REM Install NGINX Ingress Controller (skip if already installed)
echo [INFO] Checking NGINX Ingress Controller...
kubectl get namespace ingress-nginx >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [INFO] NGINX Ingress Controller already installed
) else (
    echo [INFO] Installing NGINX Ingress Controller...
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

    echo [INFO] Waiting for ingress controller to be ready (this may take a few minutes)...
    kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=300s
    if %ERRORLEVEL% neq 0 (
        echo [WARN] Ingress controller not ready yet, continuing anyway...
    ) else (
        echo [INFO] Ingress controller installed!
    )
)

REM Deploy application
echo [INFO] Deploying Daily Quote application...

kubectl apply -f "%SCRIPT_DIR%namespace.yaml"
kubectl apply -f "%SCRIPT_DIR%configmap.yaml"
kubectl apply -f "%SCRIPT_DIR%secrets.yaml"
kubectl apply -f "%SCRIPT_DIR%storage.yaml"
kubectl apply -f "%SCRIPT_DIR%api-deployment.yaml"
kubectl apply -f "%SCRIPT_DIR%frontend-deployment.yaml"

REM Try to apply ingress, with retry on failure
kubectl apply -f "%SCRIPT_DIR%ingress.yaml" 2>nul
if %ERRORLEVEL% neq 0 (
    echo [WARN] Ingress creation failed. Retrying in 10 seconds...
    timeout /t 10 /nobreak >nul
    kubectl apply -f "%SCRIPT_DIR%ingress.yaml"
)

echo [INFO] Waiting for deployments to be ready...
kubectl wait --namespace daily-quote --for=condition=available deployment --all --timeout=300s
if %ERRORLEVEL% neq 0 (
    echo [WARN] Some deployments may not be ready. Check status with: kubectl get pods -n daily-quote
)

echo [INFO] Application deployed!

REM Print access information
echo.
echo ==============================================
echo Daily Quote Application Deployed!
echo ==============================================
echo.
echo Current cluster context:
kubectl config current-context
echo.
echo Pod status:
kubectl get pods -n daily-quote
echo.
echo Add the following line to your hosts file:
echo   C:\Windows\System32\drivers\etc\hosts
echo.
echo   127.0.0.1 daily-quote.local
echo.
echo Access the application at:
echo   Public Website:    http://daily-quote.local/
echo   Admin Dashboard:   http://daily-quote.local/admin
echo   API Documentation: http://daily-quote.local/api/docs
echo.
echo Default admin credentials:
echo   Username: admin
echo   Password: admin123
echo.
echo Useful commands:
echo   kubectl get pods -n daily-quote
echo   kubectl get svc -n daily-quote
echo   kubectl logs -n daily-quote -l component=api
echo   kubectl logs -n daily-quote -l component=frontend
echo   kubectl port-forward -n daily-quote svc/daily-quote-frontend 80:80
echo ==============================================

endlocal
