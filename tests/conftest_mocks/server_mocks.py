import pytest


@pytest.fixture(autouse=True)
def mock_upload_banner(mocker):
    mocker.patch(
        "msc.services.server_service._upload_banner",
        return_value=None,
    )
