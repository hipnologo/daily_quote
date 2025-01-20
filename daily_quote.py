#!/usr/bin/env python3
import os
import git
import requests
import logging
import argparse
from datetime import datetime

# Dynamically construct the local repository path
#local_repo_path = os.path.join(os.path.expanduser('~'), 'projects/GitHub/daily_quote')
local_repo_path = os.path.dirname(os.path.abspath(__file__))

# Setup logging
logging.basicConfig(filename=os.path.join(local_repo_path, 'daily_quote.log'), level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

def generate_quote(category=None):
    """
    Generate a random quote from the specified category or from any category if not specified.
    """
    # Use exact same code from test.py
    api_url = 'https://api.api-ninjas.com/v1/quotes'
    api_key = '2JORP+gh/eyAMbtZ6/5mFQ==xkb9fNkyTI1H6xT1'
    
    try:
        response = requests.get(api_url, headers={'X-Api-Key': api_key})
        logging.info(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                quote_data = data[0]
                logging.info(f"Successfully fetched quote")
                return f"{quote_data['quote']} — {quote_data['author']}"
            else:
                logging.error("No quotes found in response")
                return None
        else:
            logging.error(f"Error: {response.status_code}, {response.text}")
            return None
            
    except Exception as e:
        logging.error(f"Exception occurred: {str(e)}")
        return None
    
# def generate_quote(category=None):
#     """
#     Generate a random quote from the specified category or from any category if not specified.

#     Args:
#         category (str, optional): The category of the quote. Defaults to None.

#     Returns:
#         str: A randomly generated quote in the format "<quote> — <author>".
#              Returns None if there was an error fetching the quote.

#     Raises:
#         requests.RequestException: If there was an error making the HTTP request.
#     """
#     api_key = os.getenv('API_NINJAS_KEY')
#     if not api_key:
#         logging.error("API_NINJAS_KEY environment variable not set")
#         return None

#     api_url = 'https://api.api-ninjas.com/v1/quotes'
#     headers = {'X-Api-Key': api_key}
    
#     # Only include category in params if it's provided
#     params = {}
#     if category:
#         params['category'] = category.lower()
#         logging.info(f"Fetching quote with category: {category}")
#     else:
#         logging.info("Fetching quote without category")

#     try:
#         logging.info(f"Making request to {api_url}")
#         if params:
#             logging.info(f"Request parameters: {params}")
#             response = requests.get(api_url, headers=headers, params=params)
#         else:
#             logging.info("No request parameters")
#             response = requests.get(api_url, headers=headers)
        
#         # Log the actual URL being called (for debugging)
#         logging.info(f"Request URL: {response.url}")
        
#         response.raise_for_status()
#         data = response.json()
        
#         if data and len(data) > 0:
#             quote_data = data[0]
#             return f"{quote_data['quote']} — {quote_data['author']}"
#         else:
#             if category:
#                 logging.error(f"No quotes found for category: {category}")
#             else:
#                 logging.error("No quotes found")
#             return None
            
#     except requests.RequestException as e:
#         if hasattr(e.response, 'text'):
#             logging.error(f"API Response: {e.response.text}")
#         logging.error(f"Error fetching quote{' for category ' + category if category else ''}: {e}")
#         return None

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
