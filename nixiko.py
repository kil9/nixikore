#!/usr/bin/python3

import random

import click
from  sqlalchemy.sql.expression import func, select

from config import log, session_scope
from model import PeriodicScript


@click.command()
@click.option('--debug', '-d', is_flag=True, default=False, help='Debug mode. No tweet if set')
def tweet(debug):
    with session_scope() as session:
        rand = random.randrange(0, session.query(PeriodicScript).count())
        row = session.query(PeriodicScript)[rand]
        log.debug(f'debug mode: {debug}')
        print(row)

@click.group()
def cli():
    log.debug('cli() called')


cli.add_command(tweet)

if __name__ == '__main__':
    cli()
