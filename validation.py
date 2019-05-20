import pickle
import pandas as pd
import numpy as np
from datetime import timedelta, date, datetime
import matplotlib.pyplot as plt
from nyt_data import get_nyt_data


# Retrieve positive/negative words
with open('positive_words.txt', 'rb') as fp:
    pos_words = pickle.load(fp)

with open('negative_words.txt', 'rb') as fp:
    neg_words = pickle.load(fp)

# Function to actually calculate sentiment based on list of pos/neg words.
def get_rule_sentiment(words):
    """
    Given a list of strings (words), return number of (pos - neg) words.
    """
    # Get number of pos/neg words
    pos = len([c for c in words if c.lower() in pos_words])
    neg = len([c for c in words if c.lower() in neg_words])
    return (pos - neg)


if __name__ == '__main__':
    api_key = "AoA9eRNg2H99U2r61TbmsEoiWxVABIjD"
    query = "Google"
    get_nyt_data(1200, api_key, query, True, "1200-pages-google.pkl")

# with open('goodstuff.txt', 'rb') as fp:
#     data = pickle.load(fp)
# print(data[0])


# df = pd.DataFrame(data, columns=['url', 'date', 'sentiment'])
# # Convert date from string to datetime
# df['date'] = pd.to_datetime(df['date'])
# # Set index as date and drop the original column
# df.index = df['date']
# df.drop(columns=['date'], inplace=True)
# print(df.head())
# # Remove NaNs
# df.fillna(0, inplace=True)
# print("Number of zeros for sentiment:", (df['sentiment'] == 0).sum(0))
