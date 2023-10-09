import logging
import time

from sqlalchemy_utils import create_database, database_exists

from msc.database import engine


logger = logging.getLogger(__name__)


def validate_database():
    """
    Check if the database exists and create it if it doesn't.
    """
    db_state = None
    if not engine.url:
        db_state = "No engine url"
    if not database_exists(engine.url):
        create_database(engine.url)
        db_state = "Database created"
    else:
        db_state = "Database already exists"

    time.sleep(1)
    engine.dispose()
    logger.info(db_state)

    return db_state
