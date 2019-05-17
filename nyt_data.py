import time
import requests
from bs4 import BeautifulSoup
import pickle
import re
from datetime import datetime
from pandas import to_datetime

# Functions to get time-series data for news articles using NYT's API for a 
# given query.


def get_nyt_article(url):
    """
    Uses BeautifulSoup to get an NYT article given its url.
    Returns title string, url string, words is list of strings.
    """
    r = requests.get(url, allow_redirects=True)
    if r.status_code >= 500:
        print("Server error! Status code:", r.status_code, "Returning...")
        return None, None, None, None
    if r.status_code >= 400 and r.status_code < 500:
        print("Bad request! Status code:", r.status_code, "Returning...")
        return None, None, None, None
    soup = BeautifulSoup(r.content, "html.parser")
    title = soup.title.get_text()
    paragraphs = "" 
    para = soup.findAll("p", {"class": "css-1ygdjhk evys1bk0"})
    for p in para:
        paragraphs += p.get_text()

    words = re.sub("[^\w]", " ", paragraphs).split()
    return (title, url, words)


def get_nyt_data(max_pages, api_key, query, pickle_bool, pickle_file_name):
    """ 
    Takes max number of pages (each page is 10 articles) to query, the api_key 
    for NYT API, and the query term.
    Returns list of tuples ()
    Optional: (boolean) pickle_bool, (string) pickle_file_name.
    If pickle, pickles list of documents to file named pickle_file_name.
    """
    print("Requesting NYT API for max {} pages for query, \"{}\".".format(max_pages, query))
    # Store all doc/publish dates as list of tuples.
    docs = []
    # First query to get number of hits.
    resp = requests.get(
        'https://api.nytimes.com/svc/search/v2/articlesearch.json',
        params={
            'q': query,
            'api-key': api_key},
    )
    rj = resp.json()
    # Response.meta.hits gives us the number of pages of results.
    hits = rj['response']['meta']['hits']
    print("NYT found {} pages.".format(hits))
    docs.extend([(x['web_url'], x['pub_date']) for x in rj["response"]["docs"]])
    c = 1
    req_start = time.time()
    # Loop for max_pages, unless there are less hits than max_pages.
    while c <= min(hits, max_pages):
        resp = requests.get(
        'https://api.nytimes.com/svc/search/v2/articlesearch.json',
        params={
            'q': query,
            'api-key': api_key,
            'page': c
            },
        )
        docs.extend([(x['web_url'], x['pub_date']) for x in rj["response"]["docs"]])
        print("Requesting page #{} of {}.".format(c, min(hits, max_pages)))
        c += 1
        # Sleep between requests to avoid hitting limit.
        time.sleep(6)

    req_finish = time.time()
    print("Finished getting document urls/dates in {}".format(req_finish - req_start))

    print("Number of docs returned from NYT:", len(docs))
    b = len(docs)
    print("Removing {} duplicates.".format(b - len(set(docs))))
    docs = list(set(docs))
    print("Extracting text from each url...")
    # List of (url, datetime, list of words)
    docs = [(d[0], to_datetime(d[1]), get_nyt_article(d[0])[2]) for d in docs]
    print("Finished extracting text from urls in {}".format(time.time() - req_finish))

    # If user requests pickle
    if (pickle_bool):
        with open(pickle_file_name, 'wb') as fp:
            pickle.dump(docs, fp)

    return docs


# HOW TO USE:
# api_key = "AoA9eRNg2H99U2r61TbmsEoiWxVABIjD"
# query = "Google"
# get_nyt_data(3, api_key, query, True, "goodstuff.txt")
