import keras
import pandas as pd
import numpy as np
import tensorflow as tf
import pickle
import random
from pprint import pprint


## Load
#dataset import
params = ['following_count', 'follower_count', 'tweet_count', 'protected', 'default_background', 'verified', 'like_count', 'defaut_profile']

dataset1 = pickle.load(open("fax.pkl", "rb" ))
dataset2 = pickle.load(open("train.pkl", "rb"))
dataset = dataset1 + dataset2

data = np.zeros(shape=(len(dataset),8), dtype=int)
output = np.zeros(shape=(len(dataset),1), dtype=int)
for j,user in enumerate(dataset):
    row = np.zeros(shape=(1,8), dtype=int)
    output[j] = 0 if user['bot_state'] == 'human' else 1
    for i,param in enumerate(params):
        row[0,i] = user[param]
    data[j] = row

test_model = tf.keras.models.load_model('faxAI')
predictions = test_model.predict(data)
print('input:')
print(data)
print('output distribution:')
print(predictions)
print('guesses:')

correct = 0
false_negative = 0
false_positive = 0
bots = 0
humans = 0
for i in range(len(predictions)):
    print(f"{np.argmax(predictions[i])} , {output[i]}")
    if output[i] == 1:
        bots += 1
    else:
        humans += 1
    if np.argmax(predictions[i]) < output[i]:
        false_negative += 1
    elif np.argmax(predictions[i]) > output[i]:
        false_positive += 1
    else:
        correct +=1
accuracy = correct / len(predictions)
rate_fp = false_positive / len(predictions)
rate_fn = false_negative / len(predictions)
print('true bot count')
print(bots)
print('true human count')
print(humans)
print('false positive rate:')
print(rate_fp)
print('false negative rate:')
print(rate_fn)
print('Accuracy rate:')
print(accuracy)
