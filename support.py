import os

import tweepy


def get_twitter_api():
    auth = tweepy.OAuthHandler(
        os.environ['TWITTER_CONSUMER_KEY'], os.environ['TWITTER_CONSUMER_SECRET'])
    auth.set_access_token(
        os.environ['TWITTER_ACCESS_KEY'], os.environ['TWITTER_ACCESS_SECRET'])
    api = tweepy.API(auth, retry_count=3, retry_delay=5, wait_on_rate_limit=True)
    return api
