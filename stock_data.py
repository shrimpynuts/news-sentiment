import requests
import pandas as pd


def get_stock_data(stock_symbol, api_key):
    """
    Gets stock data for stock_symbol using api_key for alphavantage.
    Returns a pandas dataframe.
    """
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
    st = pd.DataFrame.from_dict(raw, orient="index").reset_index(0)\
        .rename(columns={"index": "ds"})
    st.head()

    st['date'] = pd.to_datetime(st.ds)
    labels = ['1. open', '2. high', '3. low', '4. close', '5. volume']
    st[labels] = st[labels].apply(pd.to_numeric)
    st.index = st['date']
    st.drop(columns=['date'], inplace=True)
    return st


# HOW TO USE:
# api_key = "94Z49Z19XNL1GGGP"
# stock_symbol = "GOOG"
# df = get_stock_data(stock_symbol, api_key)
# print(df)
