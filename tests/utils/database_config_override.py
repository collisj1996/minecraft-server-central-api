"""
Import this before cs.db or cs.config.config is imported to
fudge the database connection settings!

This allows you to have a different database URL for the main
database and unit test database, so that they don't conflict
with each other.  When this file is imported it will override
the database connection settings with the settings specific
to the unit tests.
"""

import logging
import os

db_port = os.environ.get("UNIT_TEST_DB_PORT")
if db_port:
    logging.warning("!" * 32)
    logging.warning(f"!! Overriding DB Port to {db_port} !!")
    logging.warning("!" * 32)
    os.environ["DB_PORT"] = db_port


db_host = os.environ.get("UNIT_TEST_DB_HOST")
if db_host:
    logging.warning("!" * 32)
    logging.warning(f"!! Overriding DB Host to {db_host} !!")
    logging.warning("!" * 32)
    os.environ["DB_HOST"] = db_host
