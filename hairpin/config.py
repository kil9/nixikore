from pathlib import Path
import logging
import os

from flask import Flask


# dir
APP_HOME = Path(os.path.dirname(os.path.abspath(__file__))) / '..'

# log
log = logging.getLogger('hairpin')
lh = logging.FileHandler(APP_HOME / 'var/log/hairpin.log')
log.addHandler(lh)
