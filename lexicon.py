import requests
import time
import re
from bs4 import BeautifulSoup
import multiprocessing as mp

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import pickle


# # Building out a lexicon for news sentiment analysis
# #### Data from (https://sraf.nd.edu/textual-analysis/resources/#LM%20Sentiment%20Word%20Lists)

xls = pd.ExcelFile("data/loughran_sentiment_dictionary.xlsx")

pos = pd.read_excel(xls, "Positive")
positive_words = list(pos["ABLE"])

neg = pd.read_excel(xls, "Negative")
negative_words = list(neg["ABANDON"])

# Data also contains strong/weak modals and uncertain words.. not going to use for now, but could look into this later
unc = pd.read_excel(xls, "Uncertainty")
strong = pd.read_excel(xls, "StrongModal")
weak = pd.read_excel(xls, "WeakModal")


# #### Following data taken from (http://mpqa.cs.pitt.edu/lexicons/subj_lexicon/)
# Going to supplement the above words with this "subjective" lexicon.
subj = pd.read_csv("data/subj-clues.csv")
# Drop extra values
subj.drop(inplace=True, columns=["Unnamed: 0", "Unnamed: 2", "Unnamed: 3",	"Unnamed: 4", "Unnamed: 5",	"Unnamed: 6"])
subj.rename(inplace=True, index=str, columns={"values": "subj"})

# Functions to parse the values for word and sentiment polarity
def word(x):
    return x.split(" ")[2].split("=")[1]
def sent(x):
    if len(x.split(" ")) > 5:
        if len(x.split(" ")[5].split("=")) > 1:
            return x.split(" ")[5].split("=")[1]
        else:
            return "NaN"
    else:
        return "NaN"
    
# Transform dataframe to only have word and associated polarity
word_vect = np.vectorize(word)
sent_vect = np.vectorize(sent)
subj = subj.assign(word=lambda x: word_vect(x.subj))
subj = subj.assign(sent=lambda x: sent_vect(x.subj))
subj.drop(columns=["subj"], inplace=True)


# Now, adding these new words to our list of positive/negative words
positive_words += list(subj[subj['sent'].str.contains('positive', regex=False)]['word'])
negative_words += list(subj[subj['sent'].str.contains('negative', regex=False)]['word'])
# print(len(positive_words))
# print(len(negative_words))


# Removing duplicates
positive_words = list(set(positive_words))
negative_words = list(set(negative_words))
# print(len(set(positive_words)))
# print(len(set(negative_words)))

# Turn all words to lower case
positive_words = [x.lower() for x in positive_words]
negative_words = [x.lower() for x in negative_words]

# Take top 2500 from each set of words, to even odds between pos/neg
pos_words = positive_words[:2500]
neg_words = negative_words[:2500]


# NOTE: IN THE FUTURE ME MAY WANT TO USE SOME THESAURUS LIBRARY TO FIND EVEN MORE 
# SYNONYMS TO EXPAND OUR LEXICON

# Pickle the lexicon
with open('positive_words.txt', 'wb') as fp:
    pickle.dump(pos_words, fp)

with open('negative_words.txt', 'wb') as fp:
    pickle.dump(neg_words, fp)
