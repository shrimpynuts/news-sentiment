import pickle
import requests
import time
import re

import multiprocessing as mp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

with open ('positive_words.txt', 'rb') as fp:
    pos_words = pickle.load(fp)

with open ('negative_words.txt', 'rb') as fp:
    neg_words = pickle.load(fp)

print(pos_words[:20])
print(neg_words[:20])

# # Validation
# I am simply checking whether how many good/bad words are contained in the test files.
# Using a simple rule-based algorithm - count of positive words vs negative words (the resulting sentiment for now will simply be positive - negative word counts).

# Test files
fb = "fb-bad.txt"
fb2 = "fb-sure-bad.txt"
goog = "goog-bad.txt"
pix = "pixel-bad.txt"
uber = "uber-bad.txt"
test = "test/"
file = test + uber

def get_rule_sentiment(text):
    """ Given a string, return number of (pos, neg) words. """
    # Use regex to split text into list of words
    words = re.sub("[^\w]", " ",  text).split()
    # Get number of pos/neg words
    pos = len([c for c in words if c.lower() in pos_words])
    neg = len([c for c in words if c.lower() in neg_words])
#     print("Number of positive words:", pos)    
#     print("Number of negative words:", neg)
    return (pos - neg)
    
# with open(file) as f:
#     data = f.read()
#     print(words[:100])
#     display(get_rule_sentiment(data))



# Let's now construct a dataframe with sentiment for all documents.
# pool = mp.Pool(mp.cpu_count())
# data = [[d[0], d[1], pool.apply(get_rule_sentiment, args=())]
data = []
i = 0
count = 0
for d in docs:
    print("Processing doc #", i, "-", d[0])
    i += 1
    sent = get_rule_sentiment(get_nyt_article(d[0])[2])
    if (sent == 0):
        count += 1
#         print("WE GOT A ZERO HERE : ", count, i)
    data.append([d[0], d[1], sent])
print("Number of zeros: ", count)


df = pd.DataFrame(data, columns = ['url', 'date', 'sentiment'])

# Convert date from string to datetime
df['date'] = pd.to_datetime(df['date'])
# Set index as date and drop the original column
df.index = df['date']
df.drop(columns=['date'], inplace=True)
df.head()


# Remove NaNs
df.fillna(0, inplace=True)
print("Number of zeros for sentiment:", (df['sentiment'] == 0).sum(0))
df.astype(bool).sum(axis=0)



ax = df.plot(figsize=(12,5))


# Turns out there are duplicates resulted from NYT's API article search.

# Delete duplicates
df.drop_duplicates(subset ="url", keep=False, inplace=True) 
pd.set_option('display.max_colwidth', -1)
df[df['sentiment'] > 91]['url']



# Now, let's get the stock data.
API_URL = "https://www.alphavantage.co/query"
data = {
    "function": "TIME_SERIES_DAILY",
    "datatype": "json",
    "apikey": "94Z49Z19XNL1GGGP",
    }
data['symbol'] = "GOOG"
response = requests.get(API_URL, data)

raw = response.json()["Time Series (Daily)"]
st = pd.DataFrame.from_dict(raw, orient = "index").reset_index(0).rename(columns = {"index": "ds"})
st.head()


st['ds'] = pd.to_datetime(st.ds)
labels = ['1. open', '2. high', '3. low', '4. close', '5. volume']
st[labels] = st[labels].apply(pd.to_numeric)
st.index = st['ds']
st.drop(columns=['ds'], inplace=True)


st[datetime(2019, 3, 1):].plot(kind = "line", y = ['1. open'], figsize=(12,5))
df.plot(figsize=(12,5))
