#!/usr/bin/env python3

import random

import click

from config import db, log
from model import PeriodicScript, PendingTweet, Config, ResponseScript
from script import compile_script, process_mention
from support import get_twitter_api


@click.command()
@click.option('--debug', '-d', is_flag=True, help='Debug mode. No tweet if set')
@click.option('--count', '-c', default=1, help='Number of tweets to generate')
def generate(debug, count):
    return do_generate(debug, count)


def do_generate(debug, count, id=None, is_response=False):
    tweets = []
    for _ in range(count):
        if is_response:
            script = ResponseScript.query.filter_by(id=id).first()
        else:
            if not id:
                ind = random.randrange(0, PeriodicScript.query.count())
                script = PeriodicScript.query[ind]
            else:
                script = PeriodicScript.query.filter_by(id=id).first()

        content = script.content.replace('%{상대}', '(상대ID)')
        tweet = compile_script(content)
        pending_tweet = PendingTweet(content=tweet, image_keyword=script.image_keyword)

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


def do_tweet(debug, tweet=None, script=None):
    if script is not None:
        msg = script
        if not debug:
            api = get_twitter_api()
            api.update_status(status=tweet.content)

        msg = f'tweeted: {tweet}'
        log.info(msg)
        print(msg)
        return

    if tweet is None:
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


@click.command()
@click.option('--debug', '-d', is_flag=True, help='Debug mode. No tweet if set')
def mention(debug):
    return do_mention(debug)


def do_mention(debug):

    since_id = Config.query.filter_by(key='last_processed_mention_id').first()
    log.error(f'since_id: {since_id.value}')

    api = get_twitter_api()
    mentioned_tweets = api.mentions_timeline(since_id=int(since_id.value), count=20)
    tweets = []
    for mention in mentioned_tweets:

        if mention.user.screen_name == 'nixieko':  # prevent self mention panic :<
            continue

        tweet = process_mention(mention)
        reply_id = mention.id_str

        if not debug:
            api.update_status(status=tweet.content, in_reply_to_status_id=reply_id)

            since_id.value = reply_id
            db.session.add(since_id)

        msg = f'mention: {mention.text}'
        log.info(msg)
        print(msg)
        msg = f'response tweet: {tweet}'
        log.info(msg)
        print(msg)

        tweets.append(tweet)

        # log.error(f'mention: {mention}')
        # log.error(f'mention.text: {mention.text}')
        # log.error(f'dir(mention.user): {dir(mention.user)}')
        # log.error(f'mention.text: {mention.text}')
        # log.error(f'mention.id: {mention.id}')
        # log.error(f'mention.user.name: {mention.user.name}')
        # log.error(f'mention.user.screen_name: {mention.user.screen_name}')
        # log.error(f'mention.user.id: {mention.user.id}')
        # log.error(f'dir(mention): {dir(mention)}')

    return tweets


@click.group()
def cli():
    log.debug('cli() called')


cli.add_command(generate)
cli.add_command(tweet)
cli.add_command(mention)

if __name__ == '__main__':
    cli()
