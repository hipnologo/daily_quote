@echo off
REM Clean up Daily Quote Kubernetes deployment - Windows version
REM Usage: cleanup.bat [--cluster]

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "CLUSTER_NAME=daily-quote-cluster"
set "DELETE_CLUSTER=false"

:parse_args
if "%~1"=="" goto :end_parse
if "%~1"=="--cluster" (
    set "DELETE_CLUSTER=true"
    shift
    goto :parse_args
)
echo Unknown option: %~1
echo Usage: cleanup.bat [--cluster]
exit /b 1

:end_parse

echo [INFO] Deleting Daily Quote application resources...

kubectl delete -f "%SCRIPT_DIR%ingress.yaml" --ignore-not-found=true 2>nul
kubectl delete -f "%SCRIPT_DIR%frontend-deployment.yaml" --ignore-not-found=true 2>nul
kubectl delete -f "%SCRIPT_DIR%api-deployment.yaml" --ignore-not-found=true 2>nul
kubectl delete -f "%SCRIPT_DIR%storage.yaml" --ignore-not-found=true 2>nul
kubectl delete -f "%SCRIPT_DIR%secrets.yaml" --ignore-not-found=true 2>nul
kubectl delete -f "%SCRIPT_DIR%configmap.yaml" --ignore-not-found=true 2>nul
kubectl delete -f "%SCRIPT_DIR%namespace.yaml" --ignore-not-found=true 2>nul

echo [INFO] Application resources deleted!

if "%DELETE_CLUSTER%"=="true" (
    echo [WARN] Deleting kind cluster '%CLUSTER_NAME%'...
    kind delete cluster --name %CLUSTER_NAME%
    echo [INFO] Cluster deleted!
)

echo [INFO] Cleanup complete!

endlocal
