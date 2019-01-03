import re
import random
from enum import Enum, auto

from sqlalchemy import or_
import tossi

from config import log
from model import Word, ResponseScript
from category import Categories


class LiteralType(Enum):
    NORMAL = auto()
    EXACT_MATCH = auto()
    NUMBERS = auto()
    SELECT = auto()


class Literal():
    def __init__(self, literal):
        # self.regex_literal = re.compile(%{\w*?}')
        # self.regex_select = re.compile('%{[\w|]*?}')
        self.regex_exactmatch = re.compile('%{{\w*?}}')  # noqa:W605
        self.regex_numbers = re.compile('%{(?P<start>\d*?)\-(?P<end>\d*?)}')  # noqa:W605

        self.content = literal

        if self.regex_exactmatch.match(literal):
            self.type = LiteralType.EXACTMATCH
        elif self.regex_numbers.match(literal):
            self.type = LiteralType.NUMBERS
        elif '|' in literal:
            self.type = LiteralType.SELECT
        else:
            self.type = LiteralType.NORMAL

        self.category = literal.replace('%', '').replace('{', '').replace('}', '')

    def _process_normal(self) -> Word:
        all_categories = Categories.all_children(Categories.find_node(self.category))
        count = Word.query.filter(
                or_(Word.category == c for c in all_categories)).count()
        if count == 0:
            log.error(f'count: 0 for category {all_categories}')
            raise Exception('no entry for category')
        ind = random.randrange(0, count)
        replaced = Word.query.filter(
                or_(Word.category == c for c in all_categories))[ind]
        return replaced

    def _process_numbers(self) -> Word:
        matched = re.match(self.regex_numbers, self.content)
        start, end = matched.group('start'), matched.group('end')
        rand = random.randrange(int(start), int(end))
        return Word(content=str(rand))

    def _process_select(self) -> Word:
        selections = self.category.split('|')
        selected = random.choice(selections)
        return Word(content=selected)

    def _process_exactmatch(self) -> Word:
        count = Word.query.filter_by(category=self.category).count()
        if count == 0:
            log.error(f'count: 0 for category {self.category}')
            raise Exception(f'no entry for category {self.category}')
        ind = random.randrange(0, count)
        replaced = Word.query.filter_by(category=self.category)[ind]
        return replaced

    def replace(self):
        if self.type == LiteralType.EXACT_MATCH:
            replaced = self._process_exactmatch()
        elif self.type == LiteralType.NUMBERS:
            replaced = self._process_numbers()
        elif self.type == LiteralType.SELECT:
            replaced = self._process_select()
        else:
            replaced = self._process_normal()

        self.content = replaced.content
        return self.content


def determine_particle(word: str, particle: str) -> str:
    if not particle.startswith('('):
        return word + particle

    try:
        ret = tossi.postfix(word, particle)
    except ValueError as e:
        log.exception(e)
        return word + particle
    log.debug(f'tossi: {word} / {particle} -> {ret}')
    return ret


def find_literals(script: str):
    regex_literal = r'%{[^%{}]*?}|%{{[^%{}]*?}}|%{\d*?\-\d*?}'
    literals = re.findall(regex_literal, script)

    # remove numbered literals
    literals = (literal for literal in literals if not re.match(r'%{\d*?}', literal))
    literals = tuple(literals)

    return literals


def replace_literal_with_particle(script, literal, rep: str) -> str:
    if literal not in script:
        return script

    log.debug(f'literal: {literal} -> {rep}')
    pre_words, post_words = script.split(literal, 1)

    splitted = post_words.split(' ', 1)
    if len(splitted) == 2:
        particle, post_words = splitted
        script = pre_words + determine_particle(rep, particle) + ' ' + post_words
    else:
        script = pre_words + determine_particle(rep, post_words)
    return script


def replace_literals(script):
    return do_replace_literals(script, 0)


def do_replace_literals(script, depth):
    if depth > 10:
        log.error('depth exceed')
        return script

    literals = find_literals(script)
    if not literals:
        return script

    for i, literal in enumerate(literals):
        try:
            rep = Literal(literal).replace()
        except Exception as e:
            log.exception(e)
            log.error(f'failed to replace literal: {literal}')
            return script

        if literal not in script:
            continue

        # insert normal literal
        script = replace_literal_with_particle(script, literal, rep)

        # insert numbered literal
        numbered_literal = '%{' + str(i+1) + '}'
        while numbered_literal in script:
            script = replace_literal_with_particle(script, numbered_literal, rep)

    log.error(f'script rl: {script}')
    return do_replace_literals(script, depth+1)


def process_linefeed(script: str) -> str:
    return script.replace('\\n', '\n')


def compile_script(script: str) -> str:
    log.info(f'raw script: {script}')

    script = replace_literals(script)
    log.info(f'replaced script: {script}')

    script = process_linefeed(script)
    log.info(f'final script: {script}')
    return script


def compile_mention(script: str, mention) -> str:
    script = script.replace('%{상대}', mention.user.name)
    return script


def process_mention(mention) -> str:
    scripts = ResponseScript.query.all()

    # find candidates
    candidates = []
    for script in scripts:
        if script.keyword and script.keyword in mention.text:
            candidates.append(script)

    # determine script
    if candidates:
        script = random.choice(candidates)
    else:
        no_keyword_scripts = ResponseScript.query.filter_by(keyword=None).all()
        ind = random.randrange(0, len(no_keyword_scripts))
        script = no_keyword_scripts[ind]

    # process script
    script = compile_mention(script.content, mention)
    script = compile_script(script)

    tweet = f'@{mention.user.screen_name} {script}'
    return tweet
