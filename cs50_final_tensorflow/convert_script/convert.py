import tweepy
import csv
import pandas as pd
import numpy as np

auth = tweepy.OAuthHandler('Aa8vdSg3QVZQ9gQ3pVpMlZWX2','38uuaKNgkpDu7dIKPICZfp7rChj9SOh0hp9Ezocuojn0VuoSzX')
auth.set_access_token('1185771426885750784-axSKatOIibl15TYCSFF1HyCyAyTEpI', 'ddx1NBgaxaTCOGuGaPJ2bc7ET4b7NR4cm79NRpJaAVDWs')

#Auth
api = tweepy.API(auth)

#import list
with open('handles.csv', mode='w') as employee_file:
    handle_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, newline='')
    with open('datasets/botometer-feedback-2019.tsv/botometer-feedback-2019.tsv') as tsvfile:
        reader = csv.DictReader(tsvfile, dialect='excel-tab')
        for row in reader:
            try:
                u = api.get_user(row['id'])
                handle = u.screen_name
            except:
                continue
            if row['state'] == 'human':
                handle_writer.writerow([handle, 'human'])
            else:
                handle_writer.writerow([handle, 'bot'])