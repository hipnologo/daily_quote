@echo off
REM Port forward Daily Quote services for local development
REM Usage: port-forward.bat [service]
REM   service: frontend (default), api, or all

setlocal

set "SERVICE=%~1"
if "%SERVICE%"=="" set "SERVICE=frontend"

echo [INFO] Starting port forwarding for Daily Quote...
echo [INFO] Press Ctrl+C to stop
echo.

if /i "%SERVICE%"=="api" (
    echo [INFO] Forwarding API service to http://localhost:8000
    kubectl port-forward -n daily-quote svc/daily-quote-api 8000:8000
    goto :end
)

if /i "%SERVICE%"=="frontend" (
    echo [INFO] Forwarding Frontend service to http://localhost:8080
    echo [INFO] Access:
    echo         Public Website:  http://localhost:8080/
    echo         Admin Dashboard: http://localhost:8080/admin
    echo         API (proxied):   http://localhost:8080/api
    echo.
    kubectl port-forward -n daily-quote svc/daily-quote-frontend 8080:80
    goto :end
)

if /i "%SERVICE%"=="all" (
    echo [INFO] Starting both services in separate windows...
    start "Daily Quote - Frontend" cmd /k "kubectl port-forward -n daily-quote svc/daily-quote-frontend 8080:80"
    start "Daily Quote - API" cmd /k "kubectl port-forward -n daily-quote svc/daily-quote-api 8000:8000"
    echo.
    echo [INFO] Port forwarding started in separate windows:
    echo         Frontend: http://localhost:8080
    echo         API:      http://localhost:8000
    goto :end
)

echo [ERROR] Unknown service: %SERVICE%
echo Usage: port-forward.bat [frontend^|api^|all]

:end
endlocal
