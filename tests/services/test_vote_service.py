from datetime import datetime, timedelta

import freezegun
import pytest

from msc.models import Server, Vote
from msc.services import vote_service


def test_add_vote(session, server_colcraft: Server):
    """Tests adding a vote"""

    vote = vote_service.add_vote(
        db=session,
        server_id=server_colcraft.id,
        client_ip="127.0.0.1",
    )

    assert vote
    assert vote.server_id == server_colcraft.id


def test_one_vote_per_visitor_per_server_24_hours(session, server_colcraft: Server):
    """Tests adding a vote"""

    visitor_ip = "127.0.0.1"

    vote = vote_service.add_vote(
        db=session,
        server_id=server_colcraft.id,
        client_ip=visitor_ip,
    )

    assert session.query(Vote).count() == 1

    with pytest.raises(Exception) as e:
        vote_2 = vote_service.add_vote(
            db=session,
            server_id=server_colcraft.id,
            client_ip=visitor_ip,
        )

    assert str(e.value) == "You have already voted for this server in the last 24 hours"

    # go forward 23 hours
    with freezegun.freeze_time(datetime.utcnow() + timedelta(hours=23)):
        with pytest.raises(Exception) as e:
            vote_3 = vote_service.add_vote(
                db=session,
                server_id=server_colcraft.id,
                client_ip=visitor_ip,
            )

            assert (
                str(e.value)
                == "You have already voted for this server in the last 24 hours"
            )

    # go forward 24 hours
    with freezegun.freeze_time(datetime.utcnow() + timedelta(hours=24)):
        vote_4 = vote_service.add_vote(
            db=session,
            server_id=server_colcraft.id,
            client_ip=visitor_ip,
        )

    assert session.query(Vote).count() == 2
