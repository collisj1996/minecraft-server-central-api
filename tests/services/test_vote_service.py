from datetime import datetime, timedelta

import freezegun
import pytest

from msc.errors import NotFound
from msc.models import Server, Vote
from msc.services import server_service, vote_service


def test_add_vote(session, server_colcraft: Server):
    """Tests adding a vote"""

    vote = vote_service.add_vote(
        db=session,
        server_id=server_colcraft.id,
        client_ip="127.0.0.1",
        minecraft_username="test",
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
        minecraft_username="test",
    )

    assert session.query(Vote).count() == 1

    with pytest.raises(Exception) as e:
        vote_2 = vote_service.add_vote(
            db=session,
            server_id=server_colcraft.id,
            client_ip=visitor_ip,
            minecraft_username="alan",
        )

    assert str(e.value) == "You have already voted for this server in the last 24 hours"

    # go forward 23 hours
    with freezegun.freeze_time(datetime.utcnow() + timedelta(hours=23)):
        with pytest.raises(Exception) as e:
            vote_3 = vote_service.add_vote(
                db=session,
                server_id=server_colcraft.id,
                client_ip=visitor_ip,
                minecraft_username="alan",
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
            minecraft_username="alan",
        )

    assert session.query(Vote).count() == 2


def test_vote_for_server_flagged_for_deletion(session, server_colcraft: Server):
    """Tests adding a vote for a server flagged for deletion"""

    server_service.delete_server(
        db=session,
        user_id=server_colcraft.user_id,
        server_id=server_colcraft.id,
    )

    server_colcraft = (
        session.query(Server).filter(Server.id == server_colcraft.id).one_or_none()
    )

    assert server_colcraft.flagged_for_deletion

    with pytest.raises(NotFound):
        vote = vote_service.add_vote(
            db=session,
            server_id=server_colcraft.id,
            client_ip="1.1.1.1",
            minecraft_username="test",
        )
