#!/usr/bin/env python3

import random
import os

import click
import tweepy

from config import log, session_scope
from model import PeriodicScript
from script import compile_script


def get_twitter_api():
    auth = tweepy.OAuthHandler(
        os.environ['TWITTER_CONSUMER_KEY'], os.environ['TWITTER_CONSUMER_SECRET'])
    auth.set_access_token(
        os.environ['TWITTER_ACCESS_KEY'], os.environ['TWITTER_ACCESS_SECRET'])
    api = tweepy.API(auth, retry_count=3, retry_delay=5, wait_on_rate_limit=True)
    return api


@click.command()
@click.option('--debug', '-d', is_flag=True, help='Debug mode. No tweet if set')
def tweet(debug):
    with session_scope() as session:
        rand = random.randrange(0, session.query(PeriodicScript).count())
        script = session.query(PeriodicScript)[rand]
        log.debug(script)
        tweet = compile_script(script.contents, script.image_keyword)
        log.info(f'tweet: {tweet}')

        if not debug:
            api = get_twitter_api()
            api.update_status(status=tweet)


@click.command()
def home():
    api = get_twitter_api()
    tweets = api.home_timeline()


@click.group()
def cli():
    log.debug('cli() called')


cli.add_command(tweet)
cli.add_command(home)

if __name__ == '__main__':
    cli()
