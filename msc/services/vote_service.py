from contextlib import contextmanager
from datetime import datetime, timedelta
from uuid import UUID
from dataclasses import dataclass

from msc import db
from msc.models import Vote
from msc.errors import TooManyRequests


@dataclass
class CheckVoteInfo:
    has_voted: bool
    last_vote: datetime
    time_left_ms: int


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

    if _has_user_voted_in_last_24_hours(server_id, client_ip):
        raise TooManyRequests(
            "You have already voted for this server in the last 24 hours"
        )

    # TODO: Send vote to votifier address

    vote = Vote(server_id=server_id, client_ip_address=client_ip)

    db.session.add(vote)

    with _handle_db_errors():
        db.session.commit()

    return vote


def _has_user_voted_in_last_24_hours(
    server_id: UUID,
    client_ip: UUID,
):
    """Checks if the requesting client has voted for the server in the last 24 hours"""

    user_votes_24_hours = (
        db.session.query(Vote)
        .filter(Vote.server_id == server_id)
        .filter(Vote.client_ip_address == client_ip)
        .filter(Vote.created_at > datetime.utcnow() - timedelta(hours=24))
        .count()
    )

    return user_votes_24_hours > 0


def check_vote_info(
    server_id: UUID,
    client_ip: UUID,
) -> bool:
    """Checks if the requesting client has voted for the server in the last 24 hours"""

    has_voted = _has_user_voted_in_last_24_hours(server_id, client_ip)

    if not has_voted:
        return CheckVoteInfo(
            has_voted=False,
            last_vote=None,
            time_left_ms=None,
        )

    last_vote = (
        db.session.query(Vote)
        .filter(Vote.server_id == server_id)
        .filter(Vote.client_ip_address == client_ip)
        .order_by(Vote.created_at.desc())
        .first()
    )

    time_left_ms = int(
        (last_vote.created_at + timedelta(hours=24) - datetime.utcnow()).total_seconds()
        * 1000
    )

    return CheckVoteInfo(
        has_voted=True,
        last_vote=last_vote.created_at,
        time_left_ms=time_left_ms,
    )
