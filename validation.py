from lexicon import pos_words, neg_words
import pickle


with open ('positive_words.txt', 'rb') as fp:
    pos_words = pickle.load(fp)

with open ('negative_words.txt', 'rb') as fp:
    neg_words = pickle.load(fp)

print(pos_words[:20])
print(neg_words[:20])