import nltk
import argparse
from nltk.sentiment import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')

import os
import logging
from datetime import datetime

# Dynamically construct the local repository path
local_repo_path = os.path.join(os.path.expanduser('~'), 'projects/GitHub/daily_quote')

# Setup logging
logging.basicConfig(filename=os.path.join(local_repo_path, 'daily_quote_sentiment.log'), level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

# Set up argument parsing
parser = argparse.ArgumentParser(description='Perform sentiment analysis on quotes.')
parser.add_argument('--split', type=bool, nargs='?', const=True, default=False, help='Split output into separate files based on sentiment')
args = parser.parse_args()

# Function to perform sentiment analysis
def analyze_sentiment(text):
    """
    Analyzes the sentiment of the given text using the sentiment intensity analyzer.

    Parameters:
    text (str): The text to analyze.

    Returns:
    dict: A dictionary containing the sentiment scores for the text.
        The dictionary has the following keys:
        - 'neg': The negative sentiment score (between 0 and 1).
        - 'neu': The neutral sentiment score (between 0 and 1).
        - 'pos': The positive sentiment score (between 0 and 1).
        - 'compound': The compound sentiment score (between -1 and 1).
    """
    # Initialize the sentiment intensity analyzer
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(text)
    return sentiment

# Read text from a file
with open('quotes.txt', 'r') as file:
    quotes = file.read()

# Split the text into quotes and authors
quote_author_pairs = [quote.rsplit(" — ", 1) for quote in quotes.split("\n") if " — " in quote]
quotes = [pair[0].strip() for pair in quote_author_pairs]

# Initialize files for writing based on the split argument
if args.split:
    positive_file = open('sentiment/quotes_sentiment_positive.txt', 'w')
    negative_file = open('sentiment/quotes_sentiment_negative.txt', 'w')
    neutral_file = open('sentiment/quotes_sentiment_neutral.txt', 'w')
else:
    output_file = open('sentiment/quotes_sentiment.txt', 'w')
    
# Perform sentiment analysis on each quote and write to files
for quote, author in quote_author_pairs:
    sentiment = analyze_sentiment(quote)
    output_string = f"Quote: {quote}\nAuthor: {author}\nSentiment: {sentiment}\n\n"
    
    # Determine the highest sentiment score
    max_sentiment = max(sentiment, key=sentiment.get)
    
    if args.split:
        if max_sentiment == 'pos':
            positive_file.write(output_string)
        elif max_sentiment == 'neg':
            negative_file.write(output_string)
        else:  # max_sentiment == 'neu'
            neutral_file.write(output_string)
    else:
        output_file.write(output_string)

# Close the files
if args.split:
    positive_file.close()
    negative_file.close()
    neutral_file.close()
else:
    output_file.close()
