from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import close_all_sessions, sessionmaker

# This needs to be imported before anything in the msc package
import tests.utils.database_config_override  # noqa
from msc.app import create_app
from msc.config import config
# from msc import db
from msc.database import Database, SessionLocal, engine, get_db
from msc.migrations.db_migration import run_migrations
from msc.utils.db_utils import validate_database
from tests.conftest_fixtures.auction_fixtures import *
from tests.conftest_fixtures.server_fixtures import *
from tests.conftest_fixtures.user_fixtures import *
from tests.conftest_fixtures.vote_fixtures import *
from tests.conftest_mocks.job_mocks import *
from tests.conftest_mocks.ping_mocks import *
from tests.conftest_mocks.server_mocks import *


class DisabledSession:
    def __getattribute__(self, name) -> Any:
        raise Exception("SQLAlchemy session is disabled for testing")


def pytest_configure(config):
    # Validate the database
    validate_database()
    # Run the migrations
    run_migrations()


@pytest.fixture(scope="session")
def connection(request):
    """
    Use a single database connection for all tests.
    """
    return engine.connect()


@pytest.fixture
def session(connection, mocker):
    """
    Create a transactional fixture for each test.
    """
    # Start a transaction
    transaction = connection.begin()

    # Create a session
    db = sessionmaker(bind=connection, autoflush=False, autocommit=False)()

    yield db

    # close the session
    db.close()

    # Rollback the transaction
    if transaction.is_active:
        transaction.rollback()

    # Close all sessions
    close_all_sessions()


@pytest.fixture(scope="session")
def application():
    """
    Create a Flask app context for the tests.
    """
    return create_app()


@pytest.fixture()
def test_client(application):
    """
    Create a test client for the app.
    """
    return TestClient(application)


@pytest.fixture(autouse=True)
def disable_development_mode():
    config.development_mode = False


@pytest.fixture(autouse=True)
def disable_scheduled_jobs(mocker):
    mocker.patch("msc.app.scheduler.start", return_value=None)
