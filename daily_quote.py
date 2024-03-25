#!/usr/bin/env python3
import os
import git
import requests
import logging
from datetime import datetime

# Dynamically construct the local repository path
local_repo_path = os.path.join(os.path.expanduser('~'), 'projects/GitHub/daily_quote')

# Setup logging
logging.basicConfig(filename=os.path.join(local_repo_path, 'daily_quote.log'), level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

def generate_quote():
    try:
        response = requests.get("https://api.quotable.io/random")
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
        data = response.json()
        return f"{data['content']} — {data['author']}"
    except requests.RequestException as e:
        logging.error(f"Error fetching quote: {e}")
        return None

def daily_commit():
    quote = generate_quote()
    if quote is None:
        logging.info("No new quote fetched, skipping commit.")
        return

    quote_file = os.path.join(local_repo_path, 'quotes.txt')
    with open(quote_file, 'a') as file:
        file.write(f"{quote}\n")

    try:
        repo = git.Repo(local_repo_path)
        if repo.is_dirty(untracked_files=True):  # Check if there are changes
            repo.git.pull('origin', 'main')  # Pull latest changes to avoid conflicts
            repo.git.add(quote_file)
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            repo.index.commit(f"Daily inspirational quote update - {now}")
            repo.git.push('origin', 'main')
            logging.info("Successfully committed and pushed new quote.")
        else:
            logging.info("No changes to commit.")
    except git.exc.GitError as e:
        logging.error(f"Git operation failed: {e}")

# Execute the daily commit function
daily_commit()
