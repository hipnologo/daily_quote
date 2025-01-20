#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Path to the virtual environment in the local directory
VENV_PATH="$SCRIPT_DIR/venv"

# Try to find Python 3 in the system
if command -v python3 &>/dev/null; then
    PYTHON_PATH=$(command -v python3)
elif command -v python &>/dev/null && [[ $(python --version 2>&1) == *"Python 3"* ]]; then
    PYTHON_PATH=$(command -v python)
else
    echo "Error: Python 3 not found"
    exit 1
fi

echo "Using Python at: $PYTHON_PATH"

# Navigate to the script directory
cd "$SCRIPT_DIR"

# Check if the virtual environment exists; if not, create it and install dependencies
if [ ! -d "$VENV_PATH" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') – Virtual environment not found. Creating one..."
    $PYTHON_PATH -m venv "$VENV_PATH"
    
    # Activate the virtual environment (handle both bash and zsh)
    if [ -f "$VENV_PATH/bin/activate" ]; then
        source "$VENV_PATH/bin/activate"
    else
        echo "Error: Virtual environment activation script not found"
        exit 1
    fi
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') – Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    # Activate the virtual environment
    source "$VENV_PATH/bin/activate"
fi

# Run the Python script
echo "$(date '+%Y-%m-%d %H:%M:%S') – Running the daily_quote.py script..."
python daily_quote.py

# Check for changes in any of the quote files
if git status --porcelain | grep -q "quotes.*\.txt"; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') – Changes detected in quote files. Updating the repository..."

    # Add all quote files to the staging area
    git add quotes*.txt

    # Commit the changes with the current date and time as the commit message
    COMMIT_MESSAGE="Daily quote update: $(date '+%Y-%m-%d %H:%M:%S')"
    git commit -m "$COMMIT_MESSAGE"

    # Push the changes to the main branch
    git push origin main

    echo "$(date '+%Y-%m-%d %H:%M:%S') – Repository updated successfully."
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') – No changes detected in quote files. No update needed."
fi