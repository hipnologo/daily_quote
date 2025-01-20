# import requests
# api_url = 'https://api.api-ninjas.com/v1/quotes'
# api_key = '2JORP+gh/eyAMbtZ6/5mFQ==xkb9fNkyTI1H6xT1'
# response = requests.get(api_url, headers={'X-Api-Key': api_key})
# print(response.status_code)
# print(response.text)
# with open('quotes_new.txt', 'w') as file:
#     file.write(response.text)

import os
import logging

# Configure logging to display debug messages
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')

def test_api_key():
    api_key = os.getenv('API_NINJAS_KEY')
    if not api_key:
        logging.error("API_NINJAS_KEY environment variable not set.")
    else:
        # Log the representation to identify hidden characters
        logging.debug(f"API Key Length: {len(api_key)}")
        logging.debug(f"API Key Representation: {repr(api_key)}")
        # Optionally, compare with expected key length
        # Replace 'EXPECTED_KEY_LENGTH' with the actual length of your API key
        EXPECTED_KEY_LENGTH = 40  # Example value; adjust based on your actual key
        if len(api_key) != EXPECTED_KEY_LENGTH:
            logging.error(f"API Key length mismatch. Expected: {EXPECTED_KEY_LENGTH}, Got: {len(api_key)}")
        else:
            logging.info("API Key appears to be set correctly.")

if __name__ == "__main__":
    test_api_key()
