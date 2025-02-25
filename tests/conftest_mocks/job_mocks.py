import pytest


@pytest.fixture(autouse=True)
def mock_upload_icon(mocker):
    mocker.patch(
        "msc.services.ping_service._upload_server_icon",
        return_value=None,
    )
