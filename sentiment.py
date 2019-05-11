from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer

fb = "fb-bad.txt"
fb2 = "fb-sure-bad.txt"
goog = "goog-bad.txt"
pix = "pixel-bad.txt"
uber = "uber-bad.txt"

test = "test/"

file = test + uber

with open(file) as f:
    data = f.read()

    ### NLTK ###
    
    # Split lines
    sentences = data.splitlines()
    # Filter empty sentences
    filtered_sentences = list(filter(lambda s: len(s) > 0, sentences))

    sid = SentimentIntensityAnalyzer()
    # Cumulative score
    cum_ss = sid.polarity_scores("")
    # Calculate score for each sentence
    for s in filtered_sentences:
        print("\n\n**")
        print(s)
        print("**\n\n")
        ss = sid.polarity_scores(s)
        for k in sorted(ss):
            print('{0}: {1}, '.format(k, ss[k]),'')
            cum_ss[k] += ss[k]

    # Number of sentences processed
    n = len(filtered_sentences)
    # Get average
    for k in cum_ss:
        cum_ss[k] = cum_ss[k] / n

    all = sid.polarity_scores(data)
    print(cum_ss)
    print(all)
    # for k in sorted(cum_ss):
    #     print('{0}: {1}, '.format(k, cum_ss[k]),'')

    # for k in sorted(all):
    #     print('{0}: {1}, '.format(k, all[k]),'')

    
    ### TextBlob ### (BAD RESULTS)
    # wiki = TextBlob(data)
    # print(wiki.sentiment)
    # print(wiki.sentiment.polarity)