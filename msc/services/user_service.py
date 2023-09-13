from contextlib import contextmanager
from uuid import UUID

from msc import db
from msc.models import User


@contextmanager
def _handle_db_errors():
    """Handles database errors"""
    try:
        yield
    except Exception as e:
        db.session.rollback()
        # TODO: Raise a custom exception here
        raise e


def add_user(user_id: UUID, username: str, email: str):
    """Adds a user to the database"""

    user = User(
        id=user_id,
        username=username,
        email=email,
    )

    db.session.add(user)

    with _handle_db_errors():
        db.session.commit()

    return user
