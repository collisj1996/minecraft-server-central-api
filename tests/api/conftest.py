import pytest

from msc.database import get_db


@pytest.fixture(autouse=True)
def override_api_session(session, application, fastapi_dep):
    with fastapi_dep(application).override(
        {
            get_db: session,
        }
    ):
        yield
