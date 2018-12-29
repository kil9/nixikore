from config import log


def compile_script(script, image_keyword = None):

    log.error(type(script))
    log.error(type(image_keyword))

    script = replace_literals(script)


def replace_literals(script):
    literals = find_literals(script)

    return script


def find_literals(script):
    return ()
