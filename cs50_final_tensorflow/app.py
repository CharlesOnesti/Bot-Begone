import json
# AI Bot Filter Imports
import keras
import numpy as np
import pandas as pd
import tensorflow as tf
# Web App Imports
from tempfile import mkdtemp
from flask_session import Session
from helpers import apology, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, flash, jsonify, redirect, render_template, request, session, Response
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError

# Configure application
app = Flask(__name__)

@app.route("/checkbot", methods=["GET", "POST"])
def check_if_bot():
    if request.method == "POST":
        params = ['following_count', 'follower_count', 'tweet_count', 'protected', 'default_background', 'verified', 'like_count', 'defaut_profile']
        print("Here it all is", str(request))
        print("json", str(request.json))
        # Take the data in passed from the webserver
        harvested_data = request.json['all_of_data']
        print("harvested_data:", harvested_data)
        # Sources for AI component:
        # TensorFLow: https://www.tensorflow.org/
        # SKLearn: https://scikit-learn.org/stable/documentation.html
        # Numpy: https://numpy.org/doc/
        # Pandas: https://pandas.pydata.org/pandas-docs/stable/
        # Keras: https://keras.io/
        # Training Datasets: https://botometer.iuni.iu.edu/bot-repository/datasets.html
        data = np.zeros(shape=(len(harvested_data),8), dtype=int)
        for j,user in enumerate(harvested_data):
            row = np.zeros(shape=(1,8), dtype=int)
            for i,param in enumerate(params):
                row[0,i] = user[param]
            data[j] = row

        model = tf.keras.models.load_model('machine/PR')
        predictions = model.predict(data)
        bots_found = 0
        actual_list_thing = []
        for i in range(len(predictions)):
            if np.argmax(predictions[i]) == 1:
                actual_list_thing.append(int(np.argmax(predictions[i])))
                bots_found += 1
            else:
                actual_list_thing.append(int(np.argmax(predictions[i])))

        # Pack a header and send the data back to the webserver
        # Sources:
        # Flask response documentation: https://flask.palletsprojects.com/en/1.1.x/api/#flask.Response
        # Request headers documentation: https://requests.readthedocs.io/en/master/user/quickstart/
        print("Actual list thing", str(actual_list_thing))
        predictions_dict = {"predictions": actual_list_thing, "bots_found":str(bots_found)}
        resp = Response("Sending Data")
        resp.headers['predictions_dict'] = predictions_dict
        return resp, 200
    else:
        return "GET requests not supported", 200
