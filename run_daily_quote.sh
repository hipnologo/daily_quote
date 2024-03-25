#!/bin/bash

# Dynamically construct the path to your project directory
PROJECT_DIR="$HOME/projects/GitHub/daily_quote"

# Use the specific path to Python 3
PYTHON_PATH="/opt/homebrew/bin/python3"

# Path to the virtual environment
VENV_PATH="$PROJECT_DIR/venv"

# Navigate to the project directory
cd "$PROJECT_DIR"

# Check if the virtual environment exists; if not, create it and install dependencies
if [ ! -d "$VENV_PATH" ]; then
    echo "Virtual environment not found. Creating one..."
    $PYTHON_PATH -m venv "$VENV_PATH"
    # Activate the virtual environment
    source "$VENV_PATH/bin/activate"
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    # Activate the virtual environment
    source "$VENV_PATH/bin/activate"
fi

# Run the Python script
echo "Running the daily_quote.py script..."
python daily_quote.py

sleep 1 # Wait for the file to be written

if git status --porcelain | grep --quiet "quotes.txt"; then
    echo "Changes detected in quotes.txt. Updating the repository..."

    # Add the updated quotes.txt to the staging area
    git add quotes.txt

    # Commit the changes with the current date and time as the commit message
    COMMIT_MESSAGE="Update quotes: $(date '+%Y-%m-%d %H:%M:%S')"
    git commit -m "$COMMIT_MESSAGE"

    # Push the changes to the main branch
    git push origin main

    echo "Repository updated successfully."
else
    echo "No changes detected in quotes.txt. No update needed."
fi
