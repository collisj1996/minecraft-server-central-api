from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import close_all_sessions, sessionmaker

# This needs to be imported before anything in the msc package
import tests.utils.database_config_override  # noqa
from msc import db
from msc.app import create_app
from msc.config import config
from msc.database import Database
from msc.migrations.db_migration import run_migrations
from msc.utils.db_utils import validate_database
from tests.conftest_fixtures.server_fixtures import *
from tests.conftest_fixtures.user_fixtures import *
from tests.conftest_fixtures.vote_fixtures import *
from tests.conftest_mocks.server_mocks import *


class DisabledSession:
    def __getattribute__(self, name) -> Any:
        raise Exception("SQLAlchemy session is disabled for testing")


def pytest_configure(config):
    # Validate the database
    validate_database()
    # Run the migrations
    run_migrations()

    # Disable the sqlalchemy session
    db.session = DisabledSession()


@pytest.fixture(scope="session")
def connection(request):
    """
    Use a single database connection for all tests.
    """
    return db.engine.connect()


@pytest.fixture
def session(connection, mocker):
    """
    Create a transactional fixture for each test.
    """
    # Start a transaction
    transaction = connection.begin()

    orig_Session = db.Session
    orig_session = db.session

    db.Session = sessionmaker(
        bind=connection,
        autocommit=False,
        autoflush=False,
        join_transaction_mode="create_savepoint",
    )
    db.session = db.Session()

    # Mock the renew_session function so that it doesnt get called
    mocker.patch.object(Database, "renew_session")

    # Mock the end_session function so that it doesnt get called
    mocker.patch.object(Database, "end_session")

    yield db.session

    db.session.close()

    if transaction.is_active:
        transaction.rollback()

    close_all_sessions()

    db.session = orig_session
    db.Session = orig_Session


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


@pytest.fixture()
def disable_development_mode():
    config.development_mode = False
