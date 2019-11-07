import os
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
from contextlib import contextmanager

from flask import Flask
from flask.logging import default_handler
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# dir
APP_HOME = Path(os.path.dirname(os.path.abspath(__file__)))

# log
# LOG_FORMAT = '%(asctime)s [%(levelname).4s] %(funcName)20s / %(message)s'
LOG_FORMAT = '%(asctime)s [%(levelname).4s] %(message)s'
formatter = logging.Formatter(LOG_FORMAT)

fh = RotatingFileHandler(APP_HOME / 'var/log/nixiko.log', maxBytes=100*1024**3, backupCount=10)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(fh)

# session
# DB_PASSWORD = os.environ['DB_PASSWORD']
DB_PASSWORD = 'hdxnd0v99'
engine = create_engine(f'mysql://nixiko:{DB_PASSWORD}@localhost/nixiko?charset=utf8')
Session = sessionmaker(bind=engine)

# hairpin
hairpin_handler = RotatingFileHandler(
        APP_HOME / 'var/log/hairpin.log', maxBytes=100*1024**3, backupCount=10)
hairpin_handler.setLevel(logging.DEBUG)
hairpin_handler.setFormatter(formatter)

hairpin = Flask('hairpin')

hairpin.logger.setLevel(logging.DEBUG)
hairpin.logger.removeHandler(default_handler)
hairpin.logger.addHandler(hairpin_handler)

hairpin.secret_key = 'wLKeYeP#W3E9hgL9lXfcM@4Q'
hairpin.config['SQLALCHEMY_DATABASE_URI'] = \
    f'mysql://nixiko:{DB_PASSWORD}@localhost/nixiko?charset=utf8'
hairpin.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(hairpin)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
