from uuid import uuid4

import pytest

from msc.services import user_service


@pytest.fixture
def user_jack():
    """Returns a user with default values"""

    user = user_service.add_user(
        user_id=uuid4(),
        username="jackcollis",
        email="jackcollis@gmail.com",
    )

    return user



@pytest.fixture
def user_alan():
    """Returns a user with default values"""

    user = user_service.add_user(
        user_id=uuid4(),
        username="alansmith",
        email="alansmith@gmail.com",
    )

    return user