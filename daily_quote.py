#!/usr/bin/env python3
import os
import git
import requests
from datetime import datetime

# Dynamically construct the local repository path
home_path = os.path.expanduser('~')  # Expands to your user's home directory
local_repo_path = os.path.join(home_path, 'projects/GitHub/daily_quote')

def generate_quote():
    # Fetch a random quote from the quotable API
    response = requests.get("https://api.quotable.io/random")
    if response.status_code == 200:  # Check if the request was successful
        data = response.json()
        return f"{data['content']} — {data['author']}"
    else:
        return "No quote available today."

def daily_commit():
    quote = generate_quote()

    # Get the current date and time for the commit message
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Append the quote to a file
    with open(os.path.join(local_repo_path, 'quotes.txt'), 'a') as file:
        file.write(f"{quote}\n")
    
    # Git operations using the dynamically constructed path
    repo = git.Repo(local_repo_path)
    repo.git.add('quotes.txt')  # Specify the file you want to add
    repo.index.commit(f"Daily inspirational quote update - {now}")
    repo.git.push()

# To schedule within the script, keep the loop below:
# schedule.every().day.at("10:00").do(daily_commit)
# while True:
#     schedule.run_pending()
#     time.sleep(60)  # Wait a minute

# To schedule using cron, use the following command:
daily_commit()
