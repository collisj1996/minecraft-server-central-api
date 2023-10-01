from contextlib import contextmanager
from uuid import UUID

from sqlalchemy.orm import Session

from msc.models import User


@contextmanager
def _handle_db_errors():
    """Handles database errors"""
    try:
        yield
    except Exception as e:
        # TODO: Raise a custom exception here
        raise e


def add_user(
    db: Session,
    user_id: UUID,
    username: str,
    email: str,
):
    """Adds a user to the database"""

    user = User(
        id=user_id,
        username=username,
        email=email,
    )

    db.add(user)

    with _handle_db_errors():
        db.commit()

    return user
