# Setup
## Dependencies
import pandas as pd
import sys
import numpy as np
import tensorflow as tf
import pickle
import random

## Load
#dataset import
params = ['following_count', 'follower_count', 'tweet_count', 'protected', 'default_background', 'verified', 'like_count', 'defaut_profile']
dataset1 = pickle.load(open("train.pkl", "rb" ))
dataset2 = pickle.load(open("fax.pkl", "rb"))
dataset = dataset1 + dataset2
random.shuffle(dataset)
data = np.zeros(shape=(len(dataset),8), dtype=int)
output = np.zeros(shape=(len(dataset),1), dtype=int)
for j,user in enumerate(dataset):
    row = np.zeros(shape=(1,8), dtype=int)
    output[j] = 0 if user['bot_state'] == 'human' else 1
    for i,param in enumerate(params):
        row[0,i] = user[param]
    data[j] = row

# sklearn dependencies
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler

# One hot encoding
ohe = OneHotEncoder()
output = ohe.fit_transform(output).toarray()
# output = output.transpose()


# Split into test and train data
training_data,test_data,training_output,test_output = train_test_split(data,output,test_size = 0.01)

# Neural Net
## Dependencies
import keras
from keras.layers import Dense
from keras.models import Sequential


## Create
model = Sequential()
model.add(Dense(100, input_dim=8, activation='relu'))
model.add(Dense(50, activation='relu'))
model.add(Dense(2, activation='softmax'))

## Loss Function
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Training
history = model.fit(training_data, training_output, epochs=400, batch_size=64)

# Test the network using test data
output_prediction = model.predict(test_data)

#Converting predictions to label
prediction = list()

for i in range(len(output_prediction)):
    prediction.append(np.argmax(output_prediction[i]))

# Convert one hot encode back to class label
test = list()
for i in range(len(test_output)):
    test.append(np.argmax(test_output[i]))

# print test results
from sklearn.metrics import accuracy_score
a = accuracy_score(prediction,test)
print('Accuracy is:', a*100)

# Save the neural network
model.save('faxAI')
