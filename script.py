import re
import random
from enum import Enum, auto

from sqlalchemy import or_
import tossi

from config import log, session_scope
from model import Word
from category import Categories


class LiteralType(Enum):
    NORMAL = auto()
    MATCH_ALL = auto()
    NUMBERS = auto()


class Literal():
    def __init__(self, literal, session):
        # self.regex_literal = r'%{\w*?}'
        self.regex_matchall = r'%{{\w*?}}'
        self.regex_numbers = r'%{(?P<start>\d*?)\-(?P<end>\d*?)}'

        self.content = literal

        if re.match(self.regex_matchall, literal):
            self.type = LiteralType.MATCH_ALL
        elif re.match(self.regex_numbers, literal):
            self.type = LiteralType.NUMBERS
        else:
            self.type = LiteralType.NORMAL

        self.category = literal.replace('%', '').replace('{', '').replace('}', '')
        self.session = session

    def _process_matchall(self) -> Word:
        session = self.session
        all_categories = Categories.all_children(Categories.find_node(self.category))
        count = session.query(Word).filter(
                or_(Word.category == c for c in all_categories)).count()
        if count == 0:
            log.error(f'count: 0 for category {all_categories}')
            raise Exception('no entry for category')
        ind = random.randrange(0, count)
        replaced = session.query(Word).filter(
                or_(Word.category == c for c in all_categories))[ind]
        return replaced

    def _process_numbers(self) -> Word:
        matched = re.match(self.regex_numbers, self.content)
        start, end = matched.group('start'),matched.group('end')
        rand = random.randrange(int(start), int(end))
        return Word(contents=str(rand))

    def _process_normal(self) -> Word:
        session = self.session
        count = session.query(Word).filter_by(category=self.category).count()
        if count == 0:
            log.error(f'count: 0 for category {self.category}')
            raise Exception(f'no entry for category {self.category}')
        ind = random.randrange(0, count)
        replaced = session.query(Word).filter_by(category=self.category)[ind]
        return replaced


    def replace(self):
        if self.type == LiteralType.MATCH_ALL:
            replaced = self._process_matchall()
        elif self.type == LiteralType.NUMBERS:
            replaced = self._process_numbers()
        else:
            replaced = self._process_normal()

        rep = replace_literals(replaced.contents, self.session)
        self.content = rep
        return self.content


def determine_particle(word: str, rep: str) -> str:
    particle = word.replace(rep, '')
    if not particle.startswith('('):
        return word

    if '()' in particle:
        return word

    if '%' in word:
        return word

    parsed = tossi.parse(particle)
    log.error(f'particle: {particle}, parsed: {parsed}')

    try:
        ret = tossi.postfix(rep, particle)
    except ValueError as e:
        log.exception(e)
        return word
    log.debug(f'tossi: {rep} / {particle} -> {ret}')
    return ret


def find_literals(script: str):
    regex_literal = r'%{\w*?}|%{{\w*?}}|%{\d*?\-\d*?}'
    return re.findall(regex_literal, script)


def replace_literals(script, session):
    literals = find_literals(script)
    if not literals:
        return script

    for i, literal in enumerate(literals):
        try:
            rep = Literal(literal, session).replace()
        except Exception as e:
            log.exception(e)
            log.error(f'failed to replace literal: {literal}')
            return script
        log.debug(f'literal: {literal} -> {rep}')

        words = script.split(' ')
        log.info(f'words1: {words}')
        for i, word in enumerate(words):
            if literal in word:
                word = word.replace(literal, rep, 1)
                word = determine_particle(word, rep)
                words[i] = word
                break

        log.info(f'words2: {words}')
        script = ' '.join(words)

        numbered_literal = '%{' + str(i+1) + '}'
        if numbered_literal in script:
            script = script.replace(numbered_literal, rep)
        log.info(f'words3: {script}')

    return script


def process_linefeed(script: str) -> str:
    return script.replace('\\n', '\n')


def compile_script(script: str, image_keyword=None):
    with session_scope() as session:
        log.info(f'raw script: {script}')

        script = replace_literals(script, session)
        log.info(f'replaced script: {script}')

        script = process_linefeed(script)
        log.info(f'final script: {script}')
        return script
