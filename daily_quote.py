#!/usr/bin/env python3
import os
import git
import requests
import logging
import argparse
from datetime import datetime

# Dynamically construct the local repository path
local_repo_path = os.path.join(os.path.expanduser('~'), 'projects/GitHub/daily_quote')

# Setup logging
logging.basicConfig(filename=os.path.join(local_repo_path, 'daily_quote.log'), level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

def generate_quote(category=None):
    if category:
        # Use the new API endpoint with the specified category
        api_url = 'https://api.api-ninjas.com/v1/quotes?category={}'.format(category)
        api_key = os.getenv('API_NINJAS_KEY')
        headers = {'X-Api-Key': api_key}
        try:
            response = requests.get(api_url, headers=headers, verify=False)
            response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
            data = response.json()
            # Assuming the API returns a list of quotes, pick the first one
            if data:
                quote_data = data[0]
                return f"{quote_data['quote']} — {quote_data['author']}"
            else:
                return None
        except requests.RequestException as e:
            logging.error(f"Error fetching quote from category '{category}': {e}")
            return None
    else:
        # Use the current API endpoint
        try:
            response = requests.get("https://api.quotable.io/random", verify=False)
            response.raise_for_status()
            data = response.json()
            return f"{data['content']} — {data['author']}"
        except requests.RequestException as e:
            logging.error(f"Error fetching quote: {e}")
            return None

def daily_commit(category=None):
    quote = generate_quote(category)
    if quote is None:
        logging.info("No new quote fetched, skipping commit.")
        return

    quote_file = os.path.join(local_repo_path, 'quotes.txt')
    with open(quote_file, 'a') as file:
        file.write(f"{quote}\n")

    try:
        repo = git.Repo(local_repo_path)
        if repo.is_dirty(untracked_files=True):
            repo.git.pull('origin', 'main')
            repo.git.add(quote_file)
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            repo.index.commit(f"Daily inspirational quote update - {now}")
            repo.git.push('origin', 'main')
            logging.info("Successfully committed and pushed new quote.")
        else:
            logging.info("No changes to commit.")
    except git.exc.GitError as e:
        logging.error(f"Git operation failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and commit a daily inspirational quote. Optionally specify a category.")
    parser.add_argument('--category', type=str, help='Specify the category of the quote')
    args = parser.parse_args()

    # Execute the daily commit function with the category if provided
    daily_commit(category=args.category)
