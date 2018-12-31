import os
from pathlib import Path
import logging
from contextlib import contextmanager

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# dir
APP_HOME = Path(os.path.dirname(os.path.abspath(__file__)))


# log
# LOG_FORMAT = '%(asctime)s [%(levelname).4s] %(funcName)20s / %(message)s'
LOG_FORMAT = '%(asctime)s [%(levelname).4s] %(message)s'

logging.basicConfig(
        filename=APP_HOME / 'var/log/nixiko.log',
        level=logging.DEBUG, format=LOG_FORMAT)
log = logging.getLogger(__name__)


# session
DB_PASSWORD = os.environ['DB_PASSWORD']
engine = create_engine(f'mysql://nixiko:{DB_PASSWORD}@localhost/nixiko?charset=utf8')
Session = sessionmaker(bind=engine)

# hairpin
hairpin = Flask('hairpin')
hairpin.secret_key = 'wLKeYeP#W3E9hgL9lXfcM@4Q'
hairpin.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://nixiko:{DB_PASSWORD}@localhost/nixiko?charset=utf8'
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
