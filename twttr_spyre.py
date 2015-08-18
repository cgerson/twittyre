from spyre import server

import pandas as pd
import tweepy
from textblob import TextBlob
import os
import matplotlib
import matplotlib.dates as mdates
matplotlib.style.use('ggplot')

# commented out by Aaron!
# import matplotlib.pyplot as plt
# import json
# from requests_oauthlib import OAuth1


ACCTOK = os.environ.get('ACCTOK')
ACCTOKSEC = os.environ.get('ACCTOKSEC')
CONKEY = os.environ.get('CONKEY')
CONSEC = os.environ.get('CONSEC')
# ACCTOK = ENV['ACCTOK']
# ACCTOKSEC = ENV['ACCTOKSEC']
# CONKEY = ENV['CONKEY']
# CONSEC = ENV['CONSEC']

class TwitterExample(server.App):
    title = "Sentiment Analysis - Tweets"

    inputs = [{     "type":'text',
                    "label": 'twitter handle', 
                    "value":'go_chicken_deli',
                    "key": 'username', 
                    "action_id": "update_data"},
              { "type":'text',
                    "label": 'number of past tweets',
                "value": "10",
                    "key": 'tweet_number', 
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
        auth = tweepy.OAuthHandler(CONKEY,CONSEC)
        auth.set_access_token(ACCTOK,ACCTOKSEC)
        return tweepy.API(auth)
        
    def getData(self, params):
        api = self.twitterAPI(params)
        
        username = params['username']
        if params['tweet_number'] > 30:
            number = 30
        else:
            number = params['tweet_number']

        # in the case that handle doesn't exist
        try:
            result = api.user_timeline(username, include_rts=1, count = number)
        except:
            username = "go_chicken_deli"
            result = api.user_timeline(username, include_rts=1, count = number)

        # in the case that handle doesn't return any tweets
        if result==[]:
            username = "go_chicken_deli"
            result = api.user_timeline(username, include_rts=1, count = number)

        fav = []
        date = []
        pol = []
        subj = []
        text = []
        for tweet in result:
            fav.append(tweet.favorite_count)
            date.append(tweet.created_at)
            pol.append(TextBlob(tweet.text).sentiment[0])
            subj.append(TextBlob(tweet.text).sentiment[1])
            text.append(tweet.text)

        self.handle = api.get_user(username).name
        df = pd.DataFrame([date,pol,subj,text]).transpose()
        df.columns = ['date','polarity','subjectivity','tweet']
        df = df.reindex(index=df.index[::-1])
        return df

    def getPlot(self, params):
        number = params['tweet_number']
        df = self.getData(params).set_index('date')
        plt_obj = df[['polarity','subjectivity']].plot(kind='bar')
        plt_obj.set_ylabel("Sentiment")
        plt_obj.set_title("{0} Sentiment".format(self.handle),fontname='Helvetica')
        fig = plt_obj.get_figure()
        fig.autofmt_xdate()
        return fig

if __name__ == '__main__':
    app = TwitterExample()
    app.launch(host='0.0.0.0', port=int(os.environ.get('PORT', '5000')))
    # app.launch(port=8000)
