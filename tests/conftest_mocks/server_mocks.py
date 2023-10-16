import pytest


@pytest.fixture(autouse=True)
def mock_upload_banner(mocker):
    mocker.patch(
        "msc.services.server_service._upload_banner",
        return_value=None,
    )


@pytest.fixture(autouse=True)
def mock_is_eligible_for_auction(request, mocker):
    if "nomockgeteligibility" in request.keywords:
        return

    mocker.patch(
        "msc.services.server_service.is_eligible_for_auction",
        return_value=True,
    )
