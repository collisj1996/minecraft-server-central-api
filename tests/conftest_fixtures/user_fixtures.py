from uuid import uuid4

import pytest

from msc.services import user_service


@pytest.fixture
def user_default():
    """Returns a user with default values"""

    user = user_service.add_user(
        user_id=uuid4(),
        username="testuser",
        email="testuser@gmail.com",
    )

    return user
