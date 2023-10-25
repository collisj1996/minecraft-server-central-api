from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from msc.errors import NotFound, TooManyRequests, Unauthorized, BadRequest
from msc.models import Server, Vote, ServerHistory
from aiovotifier import VotifierClient
import asyncio
import logging
from msc.constants import SERVER_LIST_SERVICE_NAME


logger = logging.getLogger(__name__)


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
        # TODO: Raise a custom exception here
        raise e


def add_vote(
    db: Session,
    server_id: UUID,
    client_ip: UUID,
    minecraft_username: str,
):
    """Adds a vote record to a server"""

    server = (
        db.query(Server)
        .filter(
            Server.id == server_id,
            Server.flagged_for_deletion == False,
        )
        .one_or_none()
    )

    if not server:
        raise NotFound("Server not found")

    # TODO: Test this works
    if _has_username_voted_in_last_24_hours(
        db=db,
        server_id=server_id,
        minecraft_username=minecraft_username,
    ):
        raise TooManyRequests(
            "That Minecraft user has already voted for this server in the last 24 hours"
        )

    if _has_ip_voted_in_last_24_hours(
        db=db,
        server_id=server_id,
        client_ip=client_ip,
    ):
        raise TooManyRequests(
            "You have already voted for this server in the last 24 hours"
        )

    vote = Vote(
        server_id=server_id,
        client_ip_address=client_ip,
        minecraft_username=minecraft_username,
    )

    db.add(vote)

    with _handle_db_errors():
        db.commit()

    # TODO: Test this works
    if server.use_votifier:
        try:
            asyncio.run(
                _send_vote(
                    server=server,
                    minecraft_username=minecraft_username,
                    client_ip=client_ip,
                )
            )
        except Exception as e:
            logger.error("Unhandled error sending vote: ", e)
            pass

    return vote


def _has_ip_voted_in_last_24_hours(
    db: Session,
    server_id: UUID,
    client_ip: UUID,
):
    """Checks if the requesting client has voted for the server in the last 24 hours"""

    user_votes_24_hours = (
        db.query(Vote)
        .filter(Vote.server_id == server_id)
        .filter(Vote.client_ip_address == client_ip)
        .filter(Vote.created_at > datetime.utcnow() - timedelta(hours=24))
        .count()
    )

    return user_votes_24_hours > 0


def _has_username_voted_in_last_24_hours(
    db: Session,
    server_id: UUID,
    minecraft_username: str,
):
    """Checks if the requesting client has voted for the server in the last 24 hours"""

    user_votes_24_hours = (
        db.query(Vote)
        .filter(Vote.server_id == server_id)
        .filter(Vote.minecraft_username == minecraft_username)
        .filter(Vote.created_at > datetime.utcnow() - timedelta(hours=24))
        .count()
    )

    return user_votes_24_hours > 0


def check_vote_info(
    db: Session,
    server_id: UUID,
    client_ip: UUID,
) -> bool:
    """Checks if the requesting client has voted for the server in the last 24 hours"""

    has_voted = _has_ip_voted_in_last_24_hours(
        db=db,
        server_id=server_id,
        client_ip=client_ip,
    )

    if not has_voted:
        return CheckVoteInfo(
            has_voted=False,
            last_vote=None,
            time_left_ms=None,
        )

    last_vote = (
        db.query(Vote)
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


def get_total_votes(
    db: Session,
    server: Server,
):
    """Gets the total number of votes for a server"""

    total_votes = (
        db.query(Vote)
        .filter(
            Vote.server_id == server.id,
        )
        .count()
    )

    return total_votes


def get_votes_this_month(
    db: Session,
    server: Server,
):
    """Gets the total number of votes for a server this month"""

    # Get the current month and year
    now = datetime.utcnow()
    month = now.month
    year = now.year

    votes_this_month = (
        db.query(Vote)
        .filter(
            Vote.server_id == server.id,
            and_(
                func.extract("month", Vote.created_at) == month,
                func.extract("year", Vote.created_at) == year,
            ),
        )
        .count()
    )

    return votes_this_month


# TODO: Test this
def get_new_votes(
    db: Session,
    server: Server,
):
    """Gets any new votes since the last datapoint created"""

    # Get the last data point
    last_data_point = (
        db.query(ServerHistory)
        .filter(
            ServerHistory.server_id == server.id,
        )
        .order_by(
            ServerHistory.created_at.desc(),
        )
        .first()
    )

    # if no data points exist we should return all votes
    if not last_data_point:
        return (
            db.query(Vote)
            .filter(
                Vote.server_id == server.id,
            )
            .count()
        )

    # Get the number of votes after the last data point
    new_votes = (
        db.query(Vote)
        .filter(
            Vote.server_id == server.id,
            Vote.created_at > last_data_point.created_at,
        )
        .count()
    )

    return new_votes


def test_votifier(
    db: Session,
    user_id: UUID,
    server_id: UUID,
    client_ip: UUID,
    minecraft_username: str,
):
    """Tests the votifier connection"""

    server = (
        db.query(Server)
        .filter(
            Server.id == server_id,
            Server.flagged_for_deletion == False,
        )
        .one_or_none()
    )

    if not server:
        raise NotFound("Server not found")

    if server.user_id != user_id:
        raise Unauthorized("You are not authorized to test votifier on this server")

    if not server.use_votifier:
        raise BadRequest("Votifier is not enabled for this server")

    try:
        asyncio.run(
            _send_vote(
                server,
                minecraft_username,
                client_ip,
            )
        )
    except Exception as e:
        logger.error("Unhandled error sending vote: ", e)
        raise e

    return "success"


async def _send_vote(
    server: Server,
    minecraft_username: str,
    client_ip: str,
):
    """Sends a vote to the votifier server"""

    client = VotifierClient(
        host=server.votifier_ip_address,
        port=server.votifier_port,
        service_name=SERVER_LIST_SERVICE_NAME,
        secret=server.votifier_key,
    )

    response = await client.vote(
        username=minecraft_username,
        user_address=client_ip,
    )

    return response
