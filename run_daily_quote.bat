@echo off
setlocal enabledelayedexpansion

:: Get the directory where the script is located
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

:: Path to the virtual environment in the local directory
set "VENV_PATH=%SCRIPT_DIR%\venv"

:: Try to find Python 3 in the system
where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    for /f "tokens=*" %%i in ('python -c "import sys; print(sys.version_info[0])"') do set PYTHON_VERSION=%%i
    if !PYTHON_VERSION! equ 3 (
        set "PYTHON_PATH=python"
    )
) else (
    where python3 >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set "PYTHON_PATH=python3"
    ) else (
        echo Error: Python 3 not found
        exit /b 1
    )
)

echo Using Python at: %PYTHON_PATH%

:: Navigate to the script directory
cd /d "%SCRIPT_DIR%"

:: Check if the virtual environment exists; if not, create it and install dependencies
if not exist "%VENV_PATH%" (
    echo %date% %time% – Virtual environment not found. Creating one...
    %PYTHON_PATH% -m venv "%VENV_PATH%"
    
    :: Activate the virtual environment
    if exist "%VENV_PATH%\Scripts\activate.bat" (
        call "%VENV_PATH%\Scripts\activate.bat"
    ) else (
        echo Error: Virtual environment activation script not found
        exit /b 1
    )
    
    echo %date% %time% – Installing dependencies from requirements.txt...
    pip install -r requirements.txt
) else (
    :: Activate the virtual environment
    call "%VENV_PATH%\Scripts\activate.bat"
)

:: Run the Python script
echo %date% %time% – Running the daily_quote.py script...
python daily_quote.py

:: Check for changes in quote files
git status --porcelain | findstr /i "quotes.*\.txt" >nul
if %ERRORLEVEL% equ 0 (
    echo %date% %time% – Changes detected in quote files. Updating the repository...

    :: Add all quote files to the staging area
    git add quotes*.txt

    :: Get current date and time for commit message
    for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
    set "COMMIT_MESSAGE=Daily quote update: !datetime:~0,4!-!datetime:~4,2!-!datetime:~6,2! !datetime:~8,2!:!datetime:~10,2!:!datetime:~12,2!"
    
    :: Commit and push changes
    git commit -m "!COMMIT_MESSAGE!"
    git push origin main

    echo %date% %time% – Repository updated successfully.
) else (
    echo %date% %time% – No changes detected in quote files. No update needed.
)

endlocal