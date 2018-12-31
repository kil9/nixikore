#!/usr/bin/env python3

import random

import click

from config import log, session_scope
from model import PeriodicScript
from script import compile_script
from support import get_twitter_api


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


@click.group()
def cli():
    log.debug('cli() called')


cli.add_command(tweet)

if __name__ == '__main__':
    cli()
