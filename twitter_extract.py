from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream, API, Cursor

import os
from dotenv import load_dotenv

from textblob import TextBlob

# import twitter_credentials
import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt

from datetime import datetime,date

from pymongo import MongoClient

load_dotenv()

# MONGO DB CLIENT
cluster = MongoClient(f"mongodb+srv://{os.getenv('MONGO_USER')}:{os.getenv('MONGO_PW')}@cluster0.uwatv.mongodb.net/test?retryWrites=true&w=majority")
db = cluster['ChipTwitterDB']
collection = db['ChipCollection']

# TWITTER AUTHENTICATOR
class TwitterAuthenticator():
    """
    Authentication, the required variables should be contained within an .env file in the same directory
    """
    def authenticate_twitter_app(self):
        auth = OAuthHandler(os.getenv("CONSUMER_KEY"), os.getenv("CONSUMER_SECRET"))
        auth.set_access_token(os.getenv("ACCESS_TOKEN"), os.getenv("ACCESS_TOKEN_SECRET"))
        return auth


# TWITTER CLIENT
class TwitterClient():
    """
    Instantiation of a Twitter client object
    """
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)

        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets=10):
        """
        Obtaining a user's whole timeline of tweets, default limit is 5000
        """
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline
            , id=self.twitter_user, tweet_mode="extended").items():
            tweets.append(tweet)
        return tweets

    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets



# TWITTER STREAMER
class TwitterStreamer():
    """
    Class for streaming and processing live tweets.
    """
    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        # This handles twitter auth and connection to the twitter streaming API
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_authenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)

        stream.filter(track=hash_tag_list)

# TWITTER STREAM LISTENER
class TwitterListener(StreamListener):
    """
    Basic listener class that prints out received tweets to stdout
    """
    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data):
        try:
            print(data)
            with open(fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("Error on_data: %s" % str(e))
        return True

    def on_error(self, status):
        if status == 420:
            # Returning false on_data method in case rate limit occurs.
            return False
        print(status)

class TweetAnalyzer():
    """
    Functionality for analyzing and categorizing content from tweets.
    """
    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data=[tweet.retweeted_status.full_text if hasattr(tweet, "retweeted_status") else tweet.full_text for tweet in tweets ], columns=['Tweets'])
        #[tweet.full_text for tweet in tweets]

        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.full_text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])

        return df