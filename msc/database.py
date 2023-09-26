from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

from msc.config import config


def get_url():
    db_user = config.db_user
    db_pass = config.db_pass
    db_host = config.db_host
    db_port = config.db_port
    db_database = config.db_database

    return f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_database}"


engine = create_engine(get_url())

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


class Database:
    def __init__(self):
        # TODO: Remove this

        # Engine - connection to the database
        # NullPool ensures that connections are closed after use
        self.engine = create_engine(get_url(), poolclass=NullPool)

        self.Session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.renew_session()

        self.Base = declarative_base()
        self.Base.metadata.bind = self.engine

    def renew_session(self):
        # This will abandon the previous session and create a new one
        self.session = self.Session()

    def end_session(self):
        # This will close the current session
        self.session.close()
