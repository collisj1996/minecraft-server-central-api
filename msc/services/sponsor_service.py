from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from msc.constants import MINIMUM_BID_DEFAULT, SPONSORED_SLOTS_DEFAULT
from msc.errors import BadRequest, NotFound, Unauthorized
from msc.models import Sponsor, User, Server


@contextmanager
def _handle_db_errors():
    """Handles database errors"""
    try:
        yield
    except Exception as e:
        raise e


def _add_sponsor(
    db: Session,
    user_id: UUID,
    server_id: UUID,
    sponsored_year: int,
    sponsored_month: int,
    slot: int,
):
    """Adds a sponsored server to the database"""

    user = db.query(User).filter(User.id == user_id).one_or_none()

    if not user:
        raise NotFound("User not found")

    server = db.query(Server).filter(Server.id == server_id).one_or_none()

    if not server:
        raise NotFound("Server not found")

    if server.user_id != user_id:
        raise Unauthorized("User does not own server")

    sponsor = Sponsor(
        user_id=user_id,
        server_id=server_id,
        slot=slot,
        year=sponsored_year,
        month=sponsored_month,
    )

    db.add(sponsor)

    with _handle_db_errors():
        db.commit()

    return sponsor
