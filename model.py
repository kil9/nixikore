import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

from script import compile_script

Base = declarative_base()


class Config(Base):
    __tablename__ = 'config'
    key = Column(String(1024), primary_key=True)
    value = Column(String(1024))
    modified_at = Column(DateTime, default=datetime.datetime.now)


class Admin(Base):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True)
    name = Column(String(512))


class Follower(Base):
    __tablename__ = 'followers'

    id = Column(Integer, primary_key=True)
    screen_name = Column(String(256))
    mention_id = Column(String(256))
    is_blocked = Column(Integer, default=0)

    added_at = Column(DateTime, default=datetime.datetime.now)
    modified_at = Column(DateTime, default=datetime.datetime.now)


class PeriodicScript(Base):
    __tablename__ = 'periodic_scripts'

    id = Column(Integer, primary_key=True)
    contents = Column(Text)

    is_blind = Column(Integer, default=0)
    image_keyword = Column(String(1024), default=None)

    added_by = Column(String(512), default='system')
    added_at = Column(DateTime, default=datetime.datetime.now)
    modified_by = Column(String(512), default='system')
    modified_at = Column(DateTime, default=datetime.datetime.now)

    def compile(self):
        return compile_script(self.contents, self.image_keyword)

    def __repr__(self):
        form = (self.id, self.contents)
        return "<PeriodicScript[%r] %r)>" % form


class Word(Base):
    __tablename__ = 'words'

    id = Column(Integer, primary_key=True)
    contents = Column(Text)

    added_by = Column(String(512), default='system')
    added_at = Column(DateTime, default=datetime.datetime.now)
    modified_by = Column(String(512), default='system')
    modified_at = Column(DateTime, default=datetime.datetime.now)
