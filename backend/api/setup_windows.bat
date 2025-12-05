@echo off
echo Setting up Daily Quote Admin API for Windows...

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Setup completed successfully!
echo.
echo To activate the virtual environment in the future, run:
echo   venv\Scripts\activate.bat
echo.
echo To start the API server, run:
echo   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
echo.
pause
