#!/usr/bin/python3


# create scheme
from config import db
from model import *
# db.drop_all()
db.create_all()


def make_scripts():
    with open('data/script.txt') as f:
        scripts = f.readlines()

    out_scripts = [PeriodicScript(content=content.strip()) for content in scripts]

    return out_scripts


def make_words():
    with open('data/word.txt') as f:
        words = f.readlines()

    out_words = []
    for word in words:
        w = word.strip()
        splitted = w.split(' ')
        category = splitted[0]
        content = ' '.join(splitted[1:])

        out_words.append(Word(category=category, content=content))

    return out_words


def make_response_scripts():
    with open('data/response.txt') as f:
        scripts = f.readlines()

    out_scripts = [ResponseScript(content=content.strip()) for content in scripts]

    return out_scripts


def insert(data):
    for entry in data:
        db.session.add(entry)

    db.session.commit()


# insert(make_scripts())
# insert(make_words())
insert(make_response_scripts())
