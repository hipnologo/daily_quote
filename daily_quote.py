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
    """
    Generate a random quote from the specified category or from any category if not specified.

    Args:
        category (str, optional): The category of the quote. Defaults to None.

    Returns:
        str: A randomly generated quote in the format "<quote> — <author>".
             Returns None if there was an error fetching the quote.

    Raises:
        requests.RequestException: If there was an error making the HTTP request.
    """
    if category:
        api_url = 'https://api.api-ninjas.com/v1/quotes?category={}'.format(category)
        api_key = os.getenv('API_NINJAS_KEY')
        headers = {'X-Api-Key': api_key}
        try:
            response = requests.get(api_url, headers=headers, verify=False)
            response.raise_for_status()
            data = response.json()
            if data:
                quote_data = data[0]
                return f"{quote_data['quote']} — {quote_data['author']}"
            else:
                return None
        except requests.RequestException as e:
            logging.error(f"Error fetching quote from category '{category}': {e}")
            return None
    else:
        try:
            response = requests.get("https://api.quotable.io/random", verify=True)
            response.raise_for_status()
            data = response.json()
            return f"{data['content']} — {data['author']}"
        except requests.RequestException as e:
            logging.error(f"Error fetching quote: {e}")
            return None

def translate_quote(quote, target_lang):
    """
    Translate a quote to the specified language using the MyMemory API.

    Args:
        quote (str): The quote to translate.
        target_lang (str): The target language code (e.g., 'es' for Spanish, 'pt' for Portuguese).

    Returns:
        str: The translated quote.
    """
    url = "https://api.mymemory.translated.net/get"
    params = {
        "q": quote,
        "langpair": f"en|{target_lang}"
    }
    response = requests.get(url, params=params)
    translated_text = response.json()['responseData']['translatedText']
    return translated_text

def save_quotes(filename, quotes):
    """
    Save quotes to a file.

    Args:
        filename (str): The name of the file to save the quotes.
        quotes (list): The list of quotes to save.
    """
    with open(os.path.join(local_repo_path, filename), 'a') as file:
        for quote in quotes:
            file.write(f"{quote}\n")

def daily_commit(category=None):
    """
    Commits a new daily inspirational quote to a Git repository.

    Args:
        category (str, optional): The category of the quote. Defaults to None.

    Returns:
        None
    """
    quote = generate_quote(category)
    if quote is None:
        logging.info("No new quote fetched, skipping commit.")
        return

    # Save the original English quote
    save_quotes("quotes.txt", [quote])

    # Translate the quote to Spanish and Portuguese
    quote_es = translate_quote(quote, "es")
    quote_pt = translate_quote(quote, "pt")

    # Save the translated quotes
    save_quotes("quotes_es.txt", [quote_es])
    save_quotes("quotes_pt.txt", [quote_pt])

    try:
        repo = git.Repo(local_repo_path)
        if repo.is_dirty(untracked_files=True):
            repo.git.pull('origin', 'main')
            repo.git.add(all=True)
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            repo.index.commit(f"Daily inspirational quote update - {now}")
            repo.git.push('origin', 'main')
            logging.info("Successfully committed and pushed new quotes.")
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
