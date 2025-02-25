from datetime import datetime, timedelta

import freezegun
import pytest

from msc.models import Server
from msc.services import vote_service


@pytest.fixture
def votes_colcraft_20_this_month(
    session,
    server_colcraft: Server,
):
    """Returns 20 votes for colcraft this month"""

    for i in range(20):
        vote_service.add_vote(
            db=session,
            server_id=server_colcraft.id,
            client_ip=f"127.0.0.{i}",
            minecraft_username=f"test{i}",
        )


@pytest.fixture
def votes_colcraft_20_last_month(session, server_colcraft: Server):
    """Returns 20 votes for colcraft last month"""

    # using freezegun set the time to last month using timedelta
    # then add 20 votes
    with freezegun.freeze_time(datetime.utcnow() - timedelta(days=30)):
        for i in range(20):
            vote_service.add_vote(
                db=session,
                server_id=server_colcraft.id,
                client_ip=f"127.0.0.{i}",
                minecraft_username=f"test{i}",
            )
