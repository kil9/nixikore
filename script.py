import re
import random

from config import log, session_scope
from model import Word


class Literal():
    def __init__(self, literal, session = None):
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
            cat = session.query(Word).filter_by(category=self.category)[0]
        else:
            count = session.query(Word).filter_by(category=self.category).count()
            if count == 0:
                log.error(f'count: 0 for category {self.category}')
            ind = random.randrange(0, count)
            cat = session.query(Word).filter_by(category=self.category)[ind]
        log.error(f'cat: {cat}')
        self.content = cat.contents
        return self.content

def compile_script(script, image_keyword = None):
    with session_scope() as session:
        log.error(type(script))
        log.error(type(image_keyword))

        script = replace_literals(script, session)
        return script

def replace_literals(script, session):
    literals = find_literals(script)
    if not literals:
        log.error(f'script: {script}')
        return script

    for literal in literals:
        rep = Literal(literal, session).replace()
        log.error(f'literal: {literal} -> {rep}')
        script = script.replace(literal, rep, 1)

    return replace_literals(script, session)


def find_literals(script):
    regex_literal = r'%{\w*?}|%{{\w*?}}'
    return re.findall(regex_literal, script)

