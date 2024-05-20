# import spacy
# import numpy as np
# import os
# import logging
# from sklearn.decomposition import PCA
# from sklearn.manifold import TSNE
# import matplotlib.pyplot as plt
# from nltk.tokenize import word_tokenize
# from datetime import datetime
# # from gensim.models import Word2Vec

# # Load spaCy model
# nlp = spacy.load("en_core_web_md")

# # Dynamically construct the local repository path
# local_repo_path = os.path.join(os.path.expanduser('~'), 'projects/GitHub/daily_quote')

# # Setup logging
# logging.basicConfig(filename=os.path.join(local_repo_path, 'daily_quote_vectors.log'), level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

# # Assume we have a trained Word2Vec model
# # model = Word2Vec.load("word2vec.model")

# def generate_vector(quote):
#     """
#     Generate a vector representation for a given quote.

#     Parameters:
#     quote (str): The quote for which the vector representation is generated.

#     Returns:
#     numpy.ndarray: The vector representation of the quote.
#     """
#     # # Tokenize the quote
#     # words = word_tokenize(quote)

#     # # Generate a vector for the quote by averaging the vectors of its words
#     # vector = np.mean([model.wv[word] for word in words if word in model.wv], axis=0)
    
#     # Use spaCy to tokenize and generate the vector
#     doc = nlp(quote)
#     vector = doc.vector

#     return vector

# # Function to generate a random vector with a given dimension
# def generate_random_vector(dim=4):
#     """
#     Generates a random vector of given dimension.

#     Parameters:
#     dim (int): The dimension of the vector. Default is 4.

#     Returns:
#     list: A list of random numbers representing the vector.
#     """
#     return [str(round(random.uniform(0.1, 1.0), 2)) for _ in range(dim)]

# # Function to process quotes and generate files
# def process_quotes(file_path):
#     with open(file_path, 'r') as quotes_file:
#         quotes = quotes_file.readlines()

#     # Initialize lists to hold vectors and metadata
#     vectors = []
#     metadata = ["Quote\tAuthor"]

#     for quote in quotes:
#         # Split quote and author
#         quote_text, author = quote.rsplit("—", 1)
        
#         # Generate a vector for each quote
#         #vector = generate_random_vector()
#         vector = generate_vector(quote_text.strip())
#         vectors.append('\t'.join(map(str, vector)))

#         # Split quote and author
#         quote_text, author = quote.rsplit("—", 1)
#         metadata.append(f"{quote_text.strip()}\t{author.strip()}")

#     # Write vectors to a TSV file
#     os.makedirs('vectors', exist_ok=True)
#     with open(f'vectors/vectors.tsv', 'w') as vectors_file:
#         vectors_file.write('\n'.join(vectors))

#     # Write metadata to a TSV file
#     with open(f'vectors/metadata.tsv', 'w') as metadata_file:
#         metadata_file.write('\n'.join(metadata))

#     # Convert vectors to numpy array for visualization
#     vectors_np = np.array(vectors, dtype=float)
#     visualize_vectors(vectors_np, [quote.split('—')[0].strip() for quote in quotes])

# def visualize_vectors(vectors, labels):
#     """
#     Visualize high-dimensional vectors using PCA and t-SNE.

#     Parameters:
#     vectors (numpy.ndarray): The high-dimensional vectors.
#     labels (list): The labels corresponding to each vector.
#     """
#     # Reduce dimensions using PCA
#     pca = PCA(n_components=50)
#     pca_result = pca.fit_transform(vectors)

#     # Further reduce dimensions using t-SNE
#     tsne = TSNE(n_components=2, verbose=1, perplexity=40, n_iter=300)
#     tsne_result = tsne.fit_transform(pca_result)

#     # Plotting the t-SNE results
#     plt.figure(figsize=(16, 10))
#     for i, label in enumerate(labels):
#         x, y = tsne_result[i, :]
#         plt.scatter(x, y)
#         plt.annotate(label, (x, y), fontsize=9, alpha=0.75)
#     plt.title("t-SNE visualization of quotes")
    
#     # Save the plot to an image file
#     os.makedirs('images', exist_ok=True)
#     plt.savefig('images/tsne_visualization.png')
#     plt.close()

# # Replace 'quotes.txt' with the path to your actual quotes file
# process_quotes('quotes.txt')

import spacy
import numpy as np
import os
import logging
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime

# Load spaCy model
nlp = spacy.load("en_core_web_md")
# Initialize sentiment analyzer
sia = SentimentIntensityAnalyzer()

# Dynamically construct the local repository path
local_repo_path = os.path.join(os.path.expanduser('~'), 'projects/GitHub/daily_quote')

# Setup logging
logging.basicConfig(filename=os.path.join(local_repo_path, 'daily_quote_vectors.log'), level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

def generate_vector(quote):
    """
    Generate a vector representation for a given quote using spaCy.

    Parameters:
    quote (str): The quote for which the vector representation is generated.

    Returns:
    numpy.ndarray: The vector representation of the quote.
    """
    # Use spaCy to tokenize and generate the vector
    doc = nlp(quote)
    vector = doc.vector
    return vector

def analyze_sentiment(quote):
    """
    Analyze the sentiment of a given quote using VADER.

    Parameters:
    quote (str): The quote for which the sentiment is analyzed.

    Returns:
    str: The sentiment of the quote ('pos', 'neu', 'neg').
    """
    sentiment = sia.polarity_scores(quote)
    if sentiment['compound'] >= 0.05:
        return 'pos'
    elif sentiment['compound'] <= -0.05:
        return 'neg'
    else:
        return 'neu'

# Function to process quotes and generate files
def process_quotes(file_path):
    with open(file_path, 'r') as quotes_file:
        quotes = quotes_file.readlines()

    # Initialize lists to hold vectors, metadata, and sentiments
    vectors = []
    metadata = ["Quote\tAuthor"]
    sentiments = []

    for quote in quotes:
        # Split quote and author
        quote_text, author = quote.rsplit("—", 1)

        # Generate a vector for each quote
        vector = generate_vector(quote_text.strip())
        vectors.append(vector)

        # Analyze sentiment
        sentiment = analyze_sentiment(quote_text.strip())
        sentiments.append(sentiment)

        metadata.append(f"{quote_text.strip()}\t{author.strip()}")

    # Write vectors to a TSV file
    os.makedirs('vectors', exist_ok=True)
    with open('vectors/vectors.tsv', 'w') as vectors_file:
        vectors_file.write('\n'.join('\t'.join(map(str, vec)) for vec in vectors))

    # Write metadata to a TSV file
    with open('vectors/metadata.tsv', 'w') as metadata_file:
        metadata_file.write('\n'.join(metadata))
    
    # Convert vectors to numpy array for visualization
    vectors_np = np.array(vectors)
    visualize_vectors(vectors_np, sentiments)

def visualize_vectors(vectors, sentiments):
    """
    Visualize high-dimensional vectors using PCA and t-SNE.

    Parameters:
    vectors (numpy.ndarray): The high-dimensional vectors.
    sentiments (list): The sentiment labels corresponding to each vector.
    """
    # Reduce dimensions using PCA
    pca = PCA(n_components=50)
    pca_result = pca.fit_transform(vectors)

    # Further reduce dimensions using t-SNE
    tsne = TSNE(n_components=2, verbose=1, perplexity=40, n_iter=300)
    tsne_result = tsne.fit_transform(pca_result)

    # Plotting the t-SNE results
    plt.figure(figsize=(16, 10))
    colors = {'pos': 'green', 'neu': 'blue', 'neg': 'red'}
    
    # Create a dictionary for legend labels
    legend_labels = {'pos': 'Positive', 'neu': 'Neutral', 'neg': 'Negative'}
    scatter_plots = {}
    
    for i, sentiment in enumerate(sentiments):
        x, y = tsne_result[i, :]
        scatter_plots[sentiment] = plt.scatter(x, y, color=colors[sentiment], label=legend_labels[sentiment])

    # Add a legend to the plot
    handles = [scatter_plots[sentiment] for sentiment in legend_labels]
    labels = [legend_labels[sentiment] for sentiment in legend_labels]
    plt.legend(handles, labels)

    plt.title("t-SNE visualization of quotes based on sentiment")
    
    # Save the plot to an image file
    os.makedirs('images', exist_ok=True)
    plt.savefig('images/tsne_visualization_sentiment.png')
    plt.close()

# Replace 'quotes.txt' with the path to your actual quotes file
process_quotes('quotes.txt')
