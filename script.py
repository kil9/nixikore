import re
import random

from sqlalchemy import or_
import tossi

from config import log, session_scope
from model import Word
from category import Categories


class Literal():
    def __init__(self, literal, session):
        self.content = literal
        self.match_all = literal.startswith('%{{')
        self.category = literal.replace('%', '').replace('{', '').replace('}', '')
        self.session = session
        
    def replace(self):
        if not self.session:
            log.error('no session')
            return self.content

        session = self.session
        if self.match_all:
            all_categories = Categories.all_children(Categories.find_node(self.category))
            count = session.query(Word).filter(
                    or_(Word.category == c for c in all_categories)).count()
            if count == 0:
                log.error(f'count: 0 for category {all_categories}')
                return self.content
            ind = random.randrange(0, count)
            cat = session.query(Word).filter(
                    or_(Word.category == c for c in all_categories))[ind]
        else:
            count = session.query(Word).filter_by(category=self.category).count()
            if count == 0:
                log.error(f'count: 0 for category {self.category}')
                return self.content
            ind = random.randrange(0, count)
            cat = session.query(Word).filter_by(category=self.category)[ind]
        self.content = cat.contents
        return self.content

def determine_particle(word: str, rep: str) -> str:
    particle = word.replace(rep, '')
    if '(' not in particle:
        return word
    if '%' in rep:
        return word

    ret = tossi.postfix_particle(rep, particle)
    log.error(f'{rep} / {particle} -> {ret}')
    return ret

def replace_literals(script, session):
    literals = find_literals(script)
    if not literals:
        return script

    for literal in literals:
        rep = Literal(literal, session).replace()
        log.debug(f'literal: {literal} -> {rep}')

        words = script.split(' ')
        log.error(f'words1: {words}')
        out_words = []
        for i, word in enumerate(words):
            if literal in word:
                word = word.replace(literal, rep, 1)
                word = determine_particle(word, rep)
                words[i] = word
                break
        log.error(f'words2: {words}')
        script = ' '.join(words)

    return replace_literals(script, session)


def find_literals(script: str):
    regex_literal = r'%{\w*?}|%{{\w*?}}'
    return re.findall(regex_literal, script)

def compile_script(script, image_keyword = None):
    with session_scope() as session:
        log.info(f'script: {script}')
        script = replace_literals(script, session)
        log.info(f'final script: {script}')
        return script

