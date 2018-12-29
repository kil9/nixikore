#!/usr/bin/python3

import os


# create scheme
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

DB_PASSWORD = os.environ['DB_PASSWORD']
engine = create_engine(f'mysql://nixiko:{DB_PASSWORD}@localhost/nixiko?charset=utf8')

Base = declarative_base()
from model import *
Base.metadata.create_all(engine)

# add script samples
def make_scripts():
    with open('data/script.txt') as f:
        scripts = f.readlines()

    out_scripts = [PeriodicScript(contents=contents.strip()) for contents in scripts]

    return out_scripts

def make_words():
    with open('data/word.txt') as f:
        words = f.readlines()

    out_words = []
    for word in words:
        w = word.strip()
        splitted = w.split(' ')
        category = splitted[0]
        contents = ' '.join(splitted[1:])

        out_words.append(Word(category=category, contents=contents))

    return out_words

def insert(data):
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()

    for entry in data:
        session.add(entry)

    session.commit()


scripts = make_scripts()
words = make_words()
insert(scripts)
insert(words)
