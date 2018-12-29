import re

from config import log

class Literal():
    def __init__(self, literal):
        self.content = literal
        self.match_all = literal.startswith('%{{')
        self.category = literal.replace('%', '').replace('{', '').replace('}', '')
        
    def replace(self):
        return self.category


def compile_script(script, image_keyword = None):

    log.error(type(script))
    log.error(type(image_keyword))

    script = replace_literals(script)
    return script


def replace_literals(script):
    literals = find_literals(script)
    if not literals:
        log.error(f'script: {script}')
        return script

    for literal in literals:
        rep = Literal(literal).replace()
        log.error(f'literal: {literal} -> {rep}')
        script = script.replace(literal, Literal(literal).replace(), 1)

    return replace_literals(script)


def find_literals(script):
    regex_literal = r'%{\w*?}|%{{\w*?}}'
    return re.findall(regex_literal, script)
