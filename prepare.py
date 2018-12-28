# -*- code: utf-8 -*-
#!/usr/bin/python3

# create scheme
from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base

DB_PASSWORD = os.environ['DB_PASSWORD']
engine = create_engine(f'mysql://nixiko:{DB_PASSWORD}@localhost/nixiko?charset=utf8')
from model import *
# Base = declarative_base()

# Base.metadata.create_all(engine)

# add samples
with open('script.txt') as f:
    scripts = f.readlines()

periodic_scripts = [PeriodicScript(contents=script.strip()) for script in scripts]

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)

session = Session()

for script in periodic_scripts:
    session.add(script)

session.commit()
