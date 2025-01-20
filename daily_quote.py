#!/usr/bin/env python3
import os
import git
import requests
import logging
import argparse
from datetime import datetime
from urllib.parse import quote, unquote

# Dynamically construct the local repository path
#local_repo_path = os.path.join(os.path.expanduser('~'), 'projects/GitHub/daily_quote')
local_repo_path = os.path.dirname(os.path.abspath(__file__))

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
    """
    # Get API key from environment variable
    api_key = os.getenv('API_NINJAS_KEY')
    if not api_key:
        logging.error("API_NINJAS_KEY environment variable not set")
        return None

    # Clean the API key
    api_key = api_key.strip()

    # **DEBUGGING STEP**: Temporarily log the full API key
    # **Caution**: Ensure this is removed or masked after debugging to protect sensitive information
    logging.debug(f"Full API Key: '{api_key}'")  # Remove or comment out after verifying

    # Log masked version of API key for debugging
    masked_key = f"{api_key[:4]}{'*' * (len(api_key) - 4)}"
    logging.info(f"Using API key (masked): {masked_key}")

    api_url = 'https://api.api-ninjas.com/v1/quotes'
    headers = {'X-Api-Key': api_key}

    # Prepare parameters
    params = {}
    if category:
        params['category'] = category.lower()
        logging.info(f"Fetching quote with category: {category}")
    else:
        logging.info("Fetching quote without category")

    try:
        # Debug URL construction
        debug_url = api_url
        if params:
            debug_url += f"?{requests.compat.urlencode(params)}"
        logging.info(f"Making request to: {debug_url}")
        logging.info("Headers being sent (key masked): X-Api-Key: " + "*" * len(api_key))

        # Make the request
        response = requests.get(
            api_url,
            headers=headers,
            params=params if params else None,
            timeout=10
        )

        # Log response details
        logging.info(f"Response Status Code: {response.status_code}")
        logging.info(f"Response Headers: {dict(response.headers)}")

        # Check status code first
        if response.status_code != 200:
            logging.error(f"API returned status code {response.status_code}")
            logging.error(f"Response content: {response.text}")
            return None

        # Parse response
        try:
            data = response.json()
        except ValueError as e:
            logging.error(f"Failed to parse JSON response: {e}")
            logging.error(f"Raw response: {response.text}")
            return None

        # Check data
        if not data:
            logging.error("Empty response from API")
            return None

        if len(data) == 0:
            logging.error("No quotes found in response")
            return None

        # Extract quote
        quote_data = data[0]
        if not all(key in quote_data for key in ['quote', 'author']):
            logging.error(f"Incomplete quote data received: {quote_data}")
            return None

        logging.info("Successfully fetched quote")
        logging.info(f"Quote category: {quote_data.get('category', 'not specified')}")
        return f"{quote_data['quote']} — {quote_data['author']}"

    except requests.exceptions.Timeout:
        logging.error("Request timed out after 10 seconds")
        return None
    except requests.exceptions.ConnectionError as e:
        logging.error(f"Connection error occurred: {e}")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        if hasattr(e.response, 'text'):
            logging.error(f"API Response: {e.response.text}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
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
