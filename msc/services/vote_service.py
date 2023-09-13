from contextlib import contextmanager
from datetime import datetime, timedelta
from uuid import UUID

from msc import db
from msc.models import Vote


@contextmanager
def _handle_db_errors():
    """Handles database errors"""
    try:
        yield
    except Exception as e:
        db.session.rollback()
        # TODO: Raise a custom exception here
        raise e


def add_vote(
    server_id: UUID,
    client_ip: UUID,
):
    """Adds a vote record to a server"""

    visitor_votes_24_hours = (
        db.session.query(Vote)
        .filter(Vote.server_id == server_id)
        .filter(Vote.client_ip_address == client_ip)
        .filter(Vote.created_at > datetime.utcnow() - timedelta(hours=24))
        .count()
    )

    if visitor_votes_24_hours > 0:
        raise Exception("You have already voted for this server in the last 24 hours")

    # TODO: Send vote to votifier address

    vote = Vote(server_id=server_id, client_ip_address=client_ip)

    db.session.add(vote)

    with _handle_db_errors():
        db.session.commit()

    return vote
