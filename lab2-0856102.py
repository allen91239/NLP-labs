# -*- coding: utf-8 -*-
"""lab2-0856102.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/11rdeOp67p0HX8Ddk1bKBZZsztzMgkzS2

#Recommend Similar News Articles
This notebook demonstrates how to use bag-of-word vectors and cosine similarity for news article recommendation.
"""

import re
import math
import pandas as pd
import nltk
import numpy as np
from collections import Counter
from collections import defaultdict
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk import ngrams, pos_tag
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')
import spacy
nlp = spacy.load("en_core_web_sm")

"""### Get Stopwords"""

from urllib.request import urlopen
textpage = urlopen("https://raw.githubusercontent.com/bshmueli/108-nlp/master/stopwords.txt")
stopwords = list()
def zero():
  return 0
dfx = defaultdict(zero)
for line in textpage:
  decoded_line = line.decode("utf-8")
  #print(decoded_line)
  stopwords.append(decoded_line.strip("\n"))

"""#Fetching the Corpus
`get_corpus()` reads the CSV file, and then return a list of the news headlines
"""

def get_corpus(site):
  df = pd.read_csv(site) 
  print("Dataset columns", df.columns)
  print("Dataset size", len(df))
  global data_size
  data_size = len(df)
  global title
  title = df.title.to_list()
  corpus = df.content.to_list()
  return corpus

def tokenize(document):
  doc = nlp(str(document))
  return [(token.lemma_+"_"+token.pos_).lower() if not token.is_stop and (token.pos_ is not "PUNCT") and (token.pos_ is not "SPACE") else do_nothing() for token in doc]
def do_nothing():
  pass

"""use nltk's tokenizer

#Computing word frequencies
`get_vocab(corpus)` computes the word frequencies in a given corpus. It returns a list of 2-tuples. Each tuple contains the token and its frequency.
"""

def get_vocab(corpus):
  vocabulary = Counter()
  for document in corpus:
    tokens = tokenize(document)
    #doc = nlp(str(document))
    #tokens = [(token.lemma_+"_"+token.pos_).lower() if not token.is_stop and (token.pos_ is not "PUNCT") and (token.pos_ is not "SPACE") else do_nothing() for token in doc]
    for token in set(tokens):
      dfx[token] += 1
    vocabulary.update(tokens)
  #print (dfx)
  del vocabulary[None]
  del vocabulary['']
  return vocabulary

"""#Compute TFIDF Vector
`doc_to_vec(doc, vocab)` returns a TFIDF vector for document `doc`, corresponding to the presence of a word in `vocab`
"""

#def doc2vec(doc):
#  words = tokenize(doc)
#  return [1 if token in words else 0 for token, freq in vocab]

# use TFIDF instead
def doc2vec(doc):
  tfidf = np.zeros(len(vocab))
  words = tokenize(doc)
  count = defaultdict(zero)
  idx = 0
  for token, freq in vocab:
    if token in words:
      for word in words:
        if word == token:
          count[token]+=1
      tfidf[idx] = count[token]/len(words) * math.log10(data_size/dfx[token])
    else:
      tfidf[idx] = 0
    idx += 1
  return tfidf

"""Compute the TFIDF vector for each document

Cosine similarity between two numerical vectors
"""

def cosine_similarity(vec_a, vec_b):
  assert len(vec_a) == len(vec_b)
  if sum(vec_a) == 0 or sum(vec_b) == 0:
    return 0 # hack
  a_b = sum(i[0] * i[1] for i in zip(vec_a, vec_b))
  a_2 = sum([i*i for i in vec_a])
  b_2 = sum([i*i for i in vec_b])
  return a_b/(math.sqrt(a_2) * math.sqrt(b_2))

def doc_similarity(doc_a, doc_b):
  return cosine_similarity(doc2vec(doc_a), doc2vec(doc_b))

"""# Find Similar Documents
Find and print the $k$ most similar titles to a given title
"""

def k_similar(seed_id, k):
  seed_doc = corpus[seed_id]
  #seed_doc = title[seed_id]
  title_doc = title[seed_id]
  print('> "{}"'.format(title_doc))
  similarities = [doc_similarity(seed_doc, doc) for id, doc in enumerate(corpus)]
  top_indices = sorted(range(len(similarities)), key=lambda i: similarities[i])[-k:] # https://stackoverflow.com/questions/13070461/get-indices-of-the-top-n-values-of-a-list
  nearest = [[title[id], similarities[id]] for id in top_indices]
  print()
  for story in reversed(nearest):
    print('* "{}" ({})'.format(story[0], story[1]))

"""# Test our program

get_gram is a function in which the corpus is taken apart into sentences and each sentence will be tokenized. There is a dictionary that store the relationship between each token and its pos_tag. Then turn each sentence into two gram structure. Only when both words are "NNP" will the counter count them.
"""

def get_gram(corpus2):
  two_gram = Counter()
  for doc in corpus2:
    sentences = sent_tokenize(str(doc))
    for sentence in sentences:
      token_pos_dict = dict()
      tokens = word_tokenize(sentence)
      pos_tokens = pos_tag(tokens)
      twograms = list(ngrams(tokens, 2))
      for pos_token in pos_tokens:
        token_pos_dict[pos_token[0]] = pos_token[1]
      for twogram in twograms:
        if(twogram[0] != u"\u2019" and twogram[1] != u"\u2019"):
          if(token_pos_dict[twogram[0]] == 'NNP' and token_pos_dict[twogram[1]] == 'NNP'):
            nnp = [twogram[0]+' '+twogram[1]]
            #print(nnp)
            two_gram.update(nnp)
  return two_gram

print("Assignment 1:")
corpus2 = get_corpus('https://bit.ly/nlp-reuters')
two_grams = get_gram(corpus2).most_common(5)
print(two_grams)
print()
print()
print("Assignment 2:")
corpus = get_corpus('https://bit.ly/nlp-buzzfeed')
vocab = get_vocab(corpus).most_common(512)
print(vocab)
k_similar(102, 5)