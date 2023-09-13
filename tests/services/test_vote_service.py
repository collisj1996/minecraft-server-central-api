from msc.models import Server
from msc.services import vote_service


def test_add_vote(session, server_default: Server):
    """Tests adding a vote"""

    vote = vote_service.add_vote(
        server_id=server_default.id,
        client_ip="127.0.0.1",
    )

    assert vote
    assert vote.server_id == server_default.id
