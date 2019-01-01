#!/usr/bin/env python3

import random

import click

from config import db, log
from model import PeriodicScript, PendingTweet
from script import compile_script
from support import get_twitter_api


@click.command()
@click.option('--debug', '-d', is_flag=True, help='Debug mode. No tweet if set')
@click.option('--count', '-c', default=1, help='Number of tweets to generate')
def generate(debug, count):
    return do_generate(debug, count)


def do_generate(debug, count, id=None):
    tweets = []
    for _ in range(count):
        if not id:
            ind = random.randrange(0, PeriodicScript.query.count())
            script = PeriodicScript.query[ind]
        else:
            script = PeriodicScript.query.filter_by(id=id).first()

        tweet = compile_script(script.content, script.image_keyword)
        pending_tweet = PendingTweet(content=tweet)

        if not debug:
            db.session.add(pending_tweet)

        msg = f'pending tweet: {tweet}'
        log.info(msg)
        print(msg)
        tweets.append(tweet)

    if not debug:
        db.session.commit()

    log.info('done')
    print('done')

    return tweets


@click.command()
@click.option('--debug', '-d', is_flag=True, help='Debug mode. No tweet if set')
def tweet(debug):
    return do_tweet(debug)


def do_tweet(debug):
    tweet = PendingTweet.query.order_by(PendingTweet.added_at.asc()).first()
    if not tweet:
        msg = 'has no pending tweet. generate..'
        print(msg)
        log.warn(msg)
        do_generate(debug, 1)
        tweet = PendingTweet.query.order_by(PendingTweet.added_at.asc()).first()

    if not debug:
        api = get_twitter_api()
        api.update_status(status=tweet.content)

        db.session.delete(tweet)
        db.session.commit()

    msg = f'tweeted: {tweet}'
    log.info(msg)
    print(msg)


@click.group()
def cli():
    log.debug('cli() called')


cli.add_command(generate)
cli.add_command(tweet)

if __name__ == '__main__':
    cli()
