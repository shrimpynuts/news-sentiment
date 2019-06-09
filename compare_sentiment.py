from nltk.sentiment.vader import SentimentIntensityAnalyzer
import sklearn.preprocessing as preprocessing 
import matplotlib.pyplot as plt
import pandas as pd
import pickle
import requests
import lexicon 

# Functions to grab data:
def get_nltk_sentiment(words):
    """
    Calls NLTK's sentiment analyzer to get the polarity scores of words.
    """
    sid = SentimentIntensityAnalyzer()
    cc = sid.polarity_scores(words)
    return (cc['compound'])


def get_sentiments(data):
    """
    Function that gets score for text using both our own rule based bag-of-words and NLTK's model.
    The returned value should be of a dataframe of columns:
        date, liststring (all the words), delta(change in stock), rule_score, nltk_compund
    """
    data['rule_score'] = data['liststring'].map(lambda x : lexicon.get_rule_sentiment(x.lower().split(',')))
    data['nltk_compound'] = data['liststring'].map(lambda x : get_nltk_sentiment(x.replace(',', ' ')))
    return data

def get_stock(stock_symbol, api_key):
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
        "outputsize": "full"  
        }
    data['symbol'] = stock_symbol
    response = requests.get(API_URL, data)

    raw = response.json()["Time Series (Daily)"]
    st = pd.DataFrame.from_dict(raw, orient="index").reset_index(0)\
        .rename(columns={
            "index": "ds",
            "1. open": "open",
            "2. high": "high",
            "3. low": "low",
            "4. close": "close",
            "5. volume": "volume"})

    st['date'] = pd.to_datetime(st.ds)
    st.index = st['date']
    st.drop(columns=['date'], inplace=True)
    return st

# Function to concat all the data into a pandas DataFrame:
def collapse_articles(data_source = "./data/apple_data.pkl", stockName = "GOOG", 
                      time_before = '2018-09-27', time_after = '2019-05-17'):
    """
    Loads the pkl file collected from NY Times API and label each day's worth of articles
    to the next day's stock growth. 
    Weekends are skipped and handled.
    Holidays are also handled.
    
    Params: 
        time_before and time_after specify the dates to truncate the data to
    """
    #Open and load the data
    with open(data_source, "rb") as fp:   
        raw = pickle.load(fp)
    
    #------------------ Prepare Initial DataFrame ---------------
    #Prepare DataFrame.
    df = pd.DataFrame(raw, columns = ["link", "time", "words"])
    df['time'] = pd.to_datetime(df.time)
    df = df.sort_values('time').set_index('time')
    
    #Collapse weekends onto Friday
    df['dayofweek'] = df.index.dayofweek
    df.loc[df.dayofweek == 5,  'index'] = df[df.dayofweek == 5].index - pd.Timedelta(days=1)
    df.loc[df.dayofweek == 6, 'index'] = df[df.dayofweek == 6].index - pd.Timedelta(days=2)
    df.loc[(df.dayofweek != 5) & (df.dayofweek != 6),  'index'] = df[(df.dayofweek != 5) & (df.dayofweek != 6)].index
    df.drop(columns = ['link', 'index'], inplace = True)
    
    #Convert to string to get rid of none types
#     df['liststring'] = [','.join(map(str, l)).lower() if l is not None else "" for l in df['words'] ]
    df['liststring'] = [','.join(map(str, l)) if l is not None else "" for l in df['words'] ]
    
    df.drop(columns= ['words'], inplace = True)
    df = df.groupby(pd.Grouper(freq='D'))['liststring'].apply(lambda x: x.sum())
    
    #------------------- Grab Stock Data-----------------------
    #Get Stock and truncate some of the time to fit time frame.
    label = get_stock(stockName, '94Z49Z19XNL1GGGP') #Note that this is an API Key
    label = label.truncate(before=pd.Timestamp(time_before), after=pd.Timestamp(time_after))
    
    #Only use "Open" as our label.
    label['dayofweek'] = label.index.dayofweek
    label.drop(columns=['high', 'low', 'close', 'volume', 'ds'], inplace=True)
    
    # Shift dates back by 1 day, stored into column "last"
    # Handle the unique case of Monday where the delta will be taken from Friday. Not Sunday.
    label.loc[label.dayofweek == 0, 'prev_date'] = label[label.dayofweek == 0].index - pd.Timedelta(days=3)
    label.loc[label.dayofweek != 0, 'prev_date'] = label[label.dayofweek != 0].index - pd.Timedelta(days=1)
    
    #------------------- Grab Labels of Each Day -----------------------
    deltas = label.merge(label, left_on='prev_date', right_on='date', suffixes=('_left', '_right'))
    deltas.rename({'open_left':'date'}, inplace=True)
    deltas.set_index('prev_date_left', drop=True, inplace=True)
    deltas['delta'] = pd.to_numeric(deltas.open_left) - pd.to_numeric(deltas.open_right)
    deltas.drop(columns=['open_left', 'open_right', 'prev_date_right', 'dayofweek_left', 'dayofweek_right'], inplace=True)
    deltas.index.set_names(['time'], inplace=True)
    
    #------------------- Join Initial DataFrame and Labels -----------------------
    final_df = pd.DataFrame(df) 
    final_df.index = pd.to_datetime(final_df.index)
    
    #Handle weekends 
    final_df['dayofweek'] = final_df.index.dayofweek
    final_df = final_df[final_df.dayofweek != 5]
    final_df = final_df[final_df.dayofweek != 6]

    #Append delta
    final_df = pd.merge(final_df, deltas, on = 'time', how = 'inner').drop(columns = 'dayofweek')
    
    #Handle errors
    final_df = final_df[final_df['liststring']!=0] 
    
    return final_df

# Function to plot and compare the data.
def plot_data(data, normFunc, start, end, nltk):
    """
    Plot the data as specified by the normalizer function.
    Params:
        start & end specify how much data to display. The default is all
    """
    if (normFunc == "min-max"):
        scale = preprocessing.MinMaxScaler()
        print('Min Max')
    elif (normFunc == "quant"):
        scale = preprocessing.QuantileTransformer(n_quantiles=10, random_state=0)
        print('Quant')
    else:
        scale = preprocessing.StandardScaler()
        print('StandardScale: z = (x - u) / s')
        
    data = data[start:end]
    
    X = data.drop(columns = "liststring")    
    x_scale = pd.DataFrame(scale.fit_transform(X.values))
    x_scale.rename(columns = {0: "stock", 1: "rule_score", 2: 'nltk'}, inplace= True)
    
    #Drop nltk
    if (not nltk):
        x_scale.drop(columns = 'nltk', inplace = True)
    
    #Set time index back
    x_scale['date'] = X.index
    x_scale.set_index('date', inplace = True)
    
    return x_scale.plot(figsize=(10, 5))