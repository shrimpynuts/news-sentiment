import pickle
import pandas as pd
import matplotlib.pyplot as plt


def get_rule_sentiment(words):
    """
    Given a list of strings (words), return number of pos - neg words.
    """
    # Get number of pos/neg words
    pos = len([c for c in words if c.lower() in pos_words])
    neg = len([c for c in words if c.lower() in neg_words])
    return (pos - neg)

with open('goodstuff.txt', 'rb') as fp:
    data = pickle.load(fp)

print(data[0])
    
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
