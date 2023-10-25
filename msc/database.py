from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from msc.config import config


def get_url():
    db_user = config.db_user
    db_pass = config.db_pass
    db_host = config.db_host
    db_port = config.db_port
    db_database = config.db_database

    return f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_database}"


engine = create_engine(get_url(), connect_args={"options": "-c timezone=utc"})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
Base.metadata.bind = engine


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()
