import os
from pathlib import Path
import logging
from contextlib import contextmanager

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


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

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
