import pytest


@pytest.fixture(autouse=True)
def mock_poll_server(mocker):
    mocker.patch(
        "msc.services.ping_service.poll_server",
        return_value=None,
    )
