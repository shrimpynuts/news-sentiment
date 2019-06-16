import time
import requests
from bs4 import BeautifulSoup
import pickle
import re
from pandas import to_datetime
from datetime import timedelta, date, datetime
import numpy as np
import os
from multiprocessing import Pool


# Functions to get time-series data for news articles using NYT's API for a 
# given query.

api_keys = [
    # These are Will's keys (each has 10 req/min)
    ["exsr5Zr1e6ads9vR36KJxheARS9zfGyi",
    "5RM6ynn4RCoodyBYrzGM0y2geDGlPaGp",
    "7qreSl8ykg6AdgY84XI4JD5wNETvAxma",
    "Sjh4AIsDakKzlqIO98ML0QyUQxu97unv"
    ],
    # These are Johnnys's keys (each has 30 req/min)
    [
    "wDGXMKr2bFc8CAObmhtaSwT86NaChbYh",
    "AoA9eRNg2H99U2r61TbmsEoiWxVABIjD",
    "bFM0M3geSQHrjSTFaoXGFNDzb0U0Mlgl"
    ]
]

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days))[::10]:
        yield start_date + timedelta(n)


def get_nyt_article(url):
    """
    Uses BeautifulSoup to get an NYT article given its url.
    Returns title string, url string, words is list of strings.
    """
    if url == "" or len(url) == 0:
        return None
    try:
        r = requests.get(url, allow_redirects=True)
    except:
        print("Request failed, exiting with none")
        return None
    if r.status_code >= 500:
        print("Server error! Status code:", r.status_code, "Returning...")
        return None
    if r.status_code >= 400 and r.status_code < 500:
        print("Bad request! Status code:", r.status_code, "Returning...")
        return None
    soup = BeautifulSoup(r.content, "html.parser")
    title = soup.title.get_text()
    paragraphs = "" 
    
    #Notice that the class will need to be updated every once in awhile as it changes.
    para = soup.findAll("p", {"class": "css-18icg9x evys1bk0"})
    for p in para:
        paragraphs += p.get_text()

    words = re.sub("[^\w]", " ", paragraphs).split()
    return words


def process_article(article):
    """
    Article structure is (url, date).
    """
    if article[0] is not None:
        x = get_nyt_article(article[0])
        if x is not None:
            print(article[0])
            return((article[0], to_datetime(article[1]), x))


def get_nyt_data(max_pages, api_key, query, both_keys, pkl):
    """ 
    Max_pages - number of pages to search for articles (10 articles per page)
    Both_keys - True if want to use both Will + Johnny's keys
    Api_key - 1 or 0. 1 to use Johnny's, 0 to use Will's. Doesn't matter if both_keys = True
    Pkl - True to pickle, False to just return the data.
    
    Takes max number of pages (each page is 10 articles) to query, the api_key 
    for NYT API, and the query term.
    Returns list of tuples ()
    Optional: (boolean) pickle_bool, (string) pickle_file_name.
    If pickle, pickles list of documents to file named pickle_file_name.
    """
    pickle_file_name = query + "-pages=" + str(max_pages) + "-data.pkl"
    folder = "data/"
    f = folder + pickle_file_name
    f_url = folder + query + "-urls.pkl"
    req_start = time.time()

    if not os.path.isfile(f_url):
        print("Requesting NYT API for max {} pages for query, \"{}\".".format(max_pages, query))
        if both_keys:
            wait_time = 2
            keys = api_keys[1] + api_keys[0]
        else:
            if api_key == 1:
                wait_time = 1
                keys = api_keys[1]
            else:
                wait_time = 3
                keys = api_keys[0]

        print("Keys being used:", keys)
        print("Wait time:", wait_time)
        count = 0
        # Store all doc/publish dates as list of tuples.
        docs = []
        # First query to get number of hits.
        resp = requests.get(
            'https://api.nytimes.com/svc/search/v2/articlesearch.json',
            params={
                'q': query,
                'api-key': keys[count]},
        )
        rj = resp.json()
        # Response.meta.hits gives us the number of pages of results.
        hits = rj['response']['meta']['hits']
        print("NYT found {} pages.".format(hits))
        docs.extend([(x['web_url'], x['pub_date']) for x in rj["response"]["docs"]])
        c = 1

        count += 1
        time.sleep(wait_time)

        # Loop for max_pages, unless there are less hits than max_pages.
        while c <= min(hits, max_pages):
            resp = requests.get(
                'https://api.nytimes.com/svc/search/v2/articlesearch.json',
                params={
                    'q': query,
                    'api-key': keys[count],
                    'page': c,
                    # 'begin_date': begin,
                    # 'end_date': end,
                    'sort': 'newest'
                    },
            )
            count = (count + 1) % len(keys)
            # print(resp.url)
            if "response" in resp.json():
                r = [(x['web_url'], x['pub_date']) for x in resp.json()["response"]["docs"]]
                docs.extend(r)
            print("Requesting page #{} of {}.".format(c, min(hits, max_pages)), r[0])
            c += 1
            # Sleep between requests to avoid hitting limit.
            time.sleep(wait_time)

        req_finish = time.time()
        print("Finished getting document urls/dates in {}".format(req_finish - req_start))
        print("Number of docs returned from NYT:", len(docs))
        b = len(docs)
        print("Removing {} duplicates.".format(b - len(set(docs))))
        docs = list(set(docs))
        docs = list(filter(lambda x: len(x) != 0, docs))
        with open(f_url, 'wb') as fp:
                pickle.dump(docs, fp)

    else:
        print("Found pickled url's, skipping NYT API search")
        req_finish = time.time()
        with open(f_url, "rb") as fp:
            docs = pickle.load(fp)

    print("Docs: ", docs[0])
    
    print("Extracting text from each url...")
    # List of (url, datetime, list of words)
    with Pool(100) as p:
        result = p.map(process_article, docs)

    # docs = [(d[0], to_datetime(d[1]), get_nyt_article(d[0])[1]) for d in docs]
    print("Finished extracting text from urls in {}".format(time.time() - req_finish))

    # If user requests pickle
    if pkl:
        with open(f, 'wb') as fp:
            pickle.dump(result, fp)
        return None
    else:
        return docs


# HOW TO USE:
# get_nyt_data(300, 1, query, True, True, "apple-nyt.pkl")
if __name__ == "__main__":
    query = input("Enter your query: ")
    get_nyt_data(180, 0, query, True, True, True)
