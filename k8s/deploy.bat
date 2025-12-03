@echo off
REM Deploy Daily Quote application to Kubernetes (kind) - Windows version
REM Usage: deploy.bat [--build] [--clean]

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
set "CLUSTER_NAME=daily-quote-cluster"

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
echo Unknown option: %~1
echo Usage: deploy.bat [--build] [--clean]
exit /b 1

:end_parse

REM Check prerequisites
echo [INFO] Checking prerequisites...

where docker >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop.
    exit /b 1
)

where kind >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] kind is not installed. Please install kind: https://kind.sigs.k8s.io/docs/user/quick-start/#installation
    exit /b 1
)

where kubectl >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] kubectl is not installed. Please install kubectl.
    exit /b 1
)

echo [INFO] All prerequisites met!

REM Check if cluster exists
kind get clusters 2>nul | findstr /C:"%CLUSTER_NAME%" >nul
if %ERRORLEVEL% equ 0 (
    echo [INFO] Cluster '%CLUSTER_NAME%' already exists
    if "%CLEAN_DEPLOY%"=="true" (
        echo [WARN] Deleting existing cluster for clean deploy...
        kind delete cluster --name %CLUSTER_NAME%
        echo [INFO] Creating new cluster...
        kind create cluster --config "%SCRIPT_DIR%kind-config.yaml"
    )
) else (
    echo [INFO] Creating kind cluster '%CLUSTER_NAME%'...
    kind create cluster --config "%SCRIPT_DIR%kind-config.yaml"
)

REM Set kubectl context
kubectl cluster-info --context kind-%CLUSTER_NAME%

REM Build Docker images if requested
if "%BUILD_IMAGES%"=="true" (
    echo [INFO] Building Docker images...
    pushd "%PROJECT_ROOT%"
    docker-compose -f docker-compose.v2.yml build
    popd
    echo [INFO] Docker images built successfully!
)

REM Load images into kind cluster
echo [INFO] Loading images into kind cluster...
kind load docker-image daily_quote-api:latest --name %CLUSTER_NAME%
kind load docker-image daily_quote-frontend:latest --name %CLUSTER_NAME%
echo [INFO] Images loaded successfully!

REM Install NGINX Ingress Controller
echo [INFO] Installing NGINX Ingress Controller...
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

echo [INFO] Waiting for ingress controller to be ready...
kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=120s

echo [INFO] Ingress controller installed!

REM Deploy application
echo [INFO] Deploying Daily Quote application...

kubectl apply -f "%SCRIPT_DIR%namespace.yaml"
kubectl apply -f "%SCRIPT_DIR%configmap.yaml"
kubectl apply -f "%SCRIPT_DIR%secrets.yaml"
kubectl apply -f "%SCRIPT_DIR%storage.yaml"
kubectl apply -f "%SCRIPT_DIR%api-deployment.yaml"
kubectl apply -f "%SCRIPT_DIR%frontend-deployment.yaml"
kubectl apply -f "%SCRIPT_DIR%ingress.yaml"

echo [INFO] Waiting for deployments to be ready...
kubectl wait --namespace daily-quote --for=condition=available deployment --all --timeout=120s

echo [INFO] Application deployed successfully!

REM Print access information
echo.
echo ==============================================
echo Daily Quote Application Deployed!
echo ==============================================
echo.
echo Add the following line to your hosts file:
echo   C:\Windows\System32\drivers\etc\hosts
echo.
echo   127.0.0.1 daily-quote.local
echo.
echo Access the application at:
echo   http://daily-quote.local
echo.
echo API Documentation:
echo   http://daily-quote.local/api/docs
echo.
echo Default credentials:
echo   Username: admin
echo   Password: admin123
echo.
echo Useful commands:
echo   kubectl get pods -n daily-quote
echo   kubectl logs -n daily-quote -l component=api
echo   kubectl logs -n daily-quote -l component=frontend
echo ==============================================

endlocal
