# -*- coding: utf-8 -*-
"""NER

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1vgsMacK61xbHIAkDCgNUrFzA8hFmmMAE
"""

from keras.models import Model, Input
from keras.layers import LSTM, Embedding, Dense, TimeDistributed, Dropout, Bidirectional
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
from keras import metrics
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import sklearn

def read_ner_dataset(link):

    data = open(link, "r", encoding="utf8")

    corpus = []
    labels = []

    sentence = []
    label = []
    for line in data.readlines():
        if line == '\n':
            corpus.append(sentence)
            labels.append(label)

            sentence = []
            label = []
            continue

        sentence.append(line.split()[0])
        label.append(line.split()[3])

    data.close()

    sentences_entities  = []
    for i in range(len(corpus)):
        temp = []
        for j in range(len(corpus[i])):

            temp.append((corpus[i][j], labels[i][j]))
        sentences_entities.append(temp)

    return sentences_entities,corpus,labels

def get_ids(data):
  words = []

  for sent in data_train[1]:
    words.extend(sent)
  words = set(words)

  tags = []
  for tag in data_train[2]:
    tags.extend(tag)
  tags = set(tags)

  n_words = len(words)
  n_tags = len(tags)

  word2idx = {w: i + 2 for i, w in enumerate(words)}
  word2idx["UNK"] = 1
  word2idx["PAD"] = 0
  idx2word = {i: w for w, i in word2idx.items()}

  tag2idx = {t: i+1 for i, t in enumerate(tags)}
  tag2idx["PAD"] = 0

  idx2tag = {i: w for w, i in tag2idx.items()}
  
  return word2idx,tag2idx,idx2word,idx2tag

def create_model():
  BATCH_SIZE = 128  
  EPOCHS = 15  
  MAX_LEN = 40 
  EMBEDDING = 40  
  input = Input(shape=(MAX_LEN,))
  model = Embedding(input_dim=n_words+2, output_dim=EMBEDDING, 
                    input_length=MAX_LEN, mask_zero=True)(input)  
  model = Bidirectional(LSTM(units=25, return_sequences=True,
                            recurrent_dropout=0.3))(model)  
  model = TimeDistributed(Dense(50, activation="relu"))(model)  

  out = TimeDistributed(Dense(n_tags+1, activation="softmax"))(model)

  model = Model(input, out)
  model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=[metrics.categorical_accuracy])

  model.summary()
  return model

def training_model(model,word2idx,tag2idx,data_train):
  sentences = data_train[0]
  X = [[word2idx[w[0]] for w in s] for s in sentences]
  X= pad_sequences(maxlen=MAX_LEN, sequences=X, padding="post", value=word2idx["PAD"])

  y = [[tag2idx[w[1]] for w in s] for s in sentences]
  y = pad_sequences(maxlen=MAX_LEN, sequences=y, padding="post", value=tag2idx["PAD"])
  y = [to_categorical(i, num_classes=n_tags+1) for i in y]

  X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2)
  X_tr.shape, X_te.shape, np.array(y_tr).shape, np.array(y_te).shape

  history = model.fit(X_tr, np.array(y_tr), batch_size=BATCH_SIZE, 
                      epochs=EPOCHS,validation_split=0.1, validation_data=(X_te,np.array(y_te)),verbose=2)
  return history

# def eval_model(model,y_test,x_test):