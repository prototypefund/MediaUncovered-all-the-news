import os
import sys
import time
from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy import Column, Integer, Unicode, DateTime, LargeBinary
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy_utils.functions import database_exists


Base = declarative_base()


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True)
    name = Column(Unicode)
    articles = relationship("Article", backref="sources")


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)
    url = Column(Unicode, unique=False, nullable=True)
    html = Column(LargeBinary, nullable=True)

    published = Column(DateTime)
    title = Column(Unicode)
    body = Column(Unicode)

    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    source = relationship("Source")


def init(eng=None):
    if eng is None:
        eng = engine()
    Base.metadata.create_all(eng)


def session(eng=None):
    if eng is None:
        eng = engine()
    Session = sessionmaker(eng)
    return Session()


def engine(database_user=None, database_password=None, database_host=None, database_port=None, database_name=None):
    if database_user is None:
        database_user = os.environ["DATABASE_USER"]
    if database_password is None:
        database_password = os.environ["DATABASE_PASSWORD"]
    if database_host is None:
        database_host = os.environ["DATABASE_HOST"]
    if database_port is None:
        database_port = os.environ["DATABASE_PORT"]
    if database_name is None:
        database_name = os.environ["DATABASE_NAME"]

    db_url = 'postgresql://%s:%s@%s:%s/%s' % (
        database_user,
        database_password,
        database_host,
        database_port,
        database_name,
    )

    max_tries = 10
    wait_increment = 3  # in seconds
    engine = None
    for n in range(1, max_tries+1):
        try:
            if database_exists(db_url):
                engine = create_engine(db_url, echo=True, echo_pool=True,
                                       poolclass=NullPool)
        except:
            pass

        if engine is None:
            if n == max_tries:
                raise Exception("could not connect to database")

            wait_time = n * wait_increment
            print("Could not connect to database, attempt %d/%d" % (n, max_tries) +
                  "\nWaiting for %d seconds to reattempt" % wait_time)
            sys.stdout.flush()
            time.sleep(n * wait_increment)
        else:
            return engine
