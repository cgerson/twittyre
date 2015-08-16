from spyre import server

import pandas as pd
import json
import tweepy
import cnfg
from textblob import TextBlob
from requests_oauthlib import OAuth1
import matplotlib.pyplot as plt
import seaborn as sns

ACCTOK = ENV['ACCTOK']
ACCTOKSEC = ENV['ACCTOKSEC']
CONKEY = ENV['CONKEY']
CONSEC = ENV['CONSEC']

class TwitterExample(server.App):
    title = "Sentiment Analysis - Tweets"

    inputs = [{     "type":'dropdown',
                    "label": 'user', 
                    "options" : [ {"label": "Donald Trump", "value":"realDonaldTrump"},
                                  {"label": "Aaron Schumacher", "value":"planarrowspace"},
                                  {"label": "Iliad", "value":"iliadlive"},
                                  {"label": "Chicken Deli", "value":"go_chicken_deli"}],
                    "key": 'username', 
                    "action_id": "update_data"}]

    controls = [{   "type" : "hidden",
                    "id" : "update_data"}]

    tabs = ["Plot", "Table"]

    outputs = [{ "type" : "plot",
                    "id" : "plot",
                    "control_id" : "update_data",
                    "tab" : "Plot"},
                { "type" : "table",
                    "id" : "table_id",
                    "control_id" : "update_data",
                    "tab" : "Table",
                    "on_page_load" : True }]

    def twitterAPI(self,params):
        # set up twitter api config to get timeline information
        #config = cnfg.load(".twitter_config") # file with consumer keys and access tokens
        auth = tweepy.OAuthHandler(CONKEY,
                                   CONSEC)
        auth.set_access_token(ACCTOK,
                              ACCTOKSEC])
        return tweepy.API(auth)
        
    def getData(self, params):
        api = self.twitterAPI(params)
        
        username = params['username']
        result = api.user_timeline(username, include_rts=1, count = 20)

        fav = []
        date = []
        pol = []
        subj = []
        followers = []
        for tweet in result:
            fav.append(tweet.favorite_count)
            date.append(tweet.created_at)
            pol.append(TextBlob(tweet.text).sentiment[0])
            subj.append(TextBlob(tweet.text).sentiment[1])

        self.handle = api.get_user(username).name
        df = pd.DataFrame([date,pol,subj]).transpose()
        df.columns = ['date','pol','subj']
        return df

    def getPlot(self, params):
        df = self.getData(params).set_index('date')
        plt_obj = df.plot(kind='bar')
        plt_obj.set_ylabel("Sentiment")
        plt_obj.set_title(self.handle)
        fig = plt_obj.get_figure()
        return fig

if __name__ == '__main__':
    app = TwitterExample()
    app.launch(port=8000)
