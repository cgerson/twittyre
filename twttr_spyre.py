from spyre import server

import pandas as pd
import tweepy
from textblob import TextBlob
import os
import matplotlib
matplotlib.style.use('bmh')

ACCTOK = os.environ.get('ACCTOK')
ACCTOKSEC = os.environ.get('ACCTOKSEC')
CONKEY = os.environ.get('CONKEY')
CONSEC = os.environ.get('CONSEC')


class TwitterExample(server.App):
    title = "Sentiment Analysis - Tweets"
    
    inputs = [{     "type":'text',
                    "label": 'twitter handle', 
                    "value":'go_chicken_deli',
                    "key": 'username', 
                    "action_id": "update_data"},
              { "type":'text',
                    "label": 'max number of past tweets',
                "value": 10,
                    "key": 'tweet_number', 
                    "action_id": "refresh"},
              { "type":'dropdown',
                "label":'include retweets',
                    "options" : [{"label": "no", "value":False},
                                 {"label": "yes", "value":True}],
                    "key": 'retweets', 
                    "action_id": "refresh"}]

    controls = [{   "type" : "button",
                    "label":"refresh",
                    "id" : "refresh"},
                {   "type" : "hidden",
                    "id" : "update_data"}]

    tabs = ["Plot", "Tweets","About"]

    outputs = [{ "type" : "plot",
                    "id" : "plot",
                    "control_id" : "refresh",
                    "tab" : "Plot"},
                { "type" : "table",
                    "id" : "table_id",
                    "control_id" : "refresh",
                    "tab" : "Tweets",
                    "on_page_load" : True },
               { "type" : "html",
                    "id" : "simple_html_output",
                    "control_id" : "update_data",
                    "tab" : "About"}]

    def twitterAPI(self,params):
        ''' set up twitter api config to get timeline information'''
        
        auth = tweepy.OAuthHandler(CONKEY,CONSEC)
        auth.set_access_token(ACCTOK,ACCTOKSEC)
        return tweepy.API(auth)
        
    def getData(self, params):
        ''' return table of tweets with associated polarity and subjectivity score '''
        
        api = self.twitterAPI(params)
        rt = params['retweets']
        username = params['username']
        
        if int(params['tweet_number']) > 30:
            number = 30
        else:
            number = params['tweet_number']

        # in the case that handle doesn't exist
        try:
            result = api.user_timeline(username, include_rts=rt, count = number)
        except:
            username = "go_chicken_deli"
            result = api.user_timeline(username, include_rts=rt, count = number)

        # in the case that handle doesn't return any tweets
        if result==[]:
            username = "go_chicken_deli"
            result = api.user_timeline(username, include_rts=rt, count = number)

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
        df.columns = ['Date','polarity','subjectivity','tweet']
        return df

    def getPlot(self, params):
        ''' return matplotlib figure of polarity and subjectivity of tweets in timeline '''
        
        df = self.getData(params)
        df = df.reindex(index=df.index[::-1]).set_index('Date')
        plt_obj = df[['polarity','subjectivity']].plot(kind='bar',ylim=(-1.0,1.0),grid=True,rot=0)
        plt_obj.set_ylabel("Sentiment")
        plt_obj.set_title("{0} Sentiment\n(polarity between -1.0 & 1.0, subjectivity between 0 & 1.0)\n".format(self.handle),fontname='Helvetica')
        plt_obj.tick_params(axis='both', which='major', labelsize=14)
        fig = plt_obj.get_figure()
        fig.set_size_inches(16.5, 8.5)
        fig.autofmt_xdate()
        return fig

    def getHTML(self,params):
        ''' return html for 'About' tab '''
        
        html = '''
        <style>
            body {
                background-image: url("http://www.photos-public-domain.com/wp-content/uploads/2011/09/baby-blue-leather-texture.jpg");
            }
        </style>
        <br>
        <pre>Sentiment Analysis by <a href='https://textblob.readthedocs.org/en/dev/index.html' target='_blank'>TextBlob</a>.</pre>
        <br>
        <pre>App by <a href = 'https://github.com/cgerson' target='_blank'>Claire Gerson</a>.</pre>
        '''
        return html
        
if __name__ == '__main__':
    app = TwitterExample()
    pd.set_option('display.max_colwidth', -1) #displays full tweet text
    app.launch(host='0.0.0.0', port=int(os.environ.get('PORT', '5000')))
    # app.launch(port=8000)
