from contextlib import contextmanager
from uuid import UUID

from sqlalchemy.orm import Session

from msc.models import User
from msc.errors import NotFound


class UserNotFound(NotFound):
    """User not found error"""

    pass


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


def get_user(
    db: Session,
    user_id: UUID,
):
    """Gets a user from the database"""

    user = db.query(User).filter(User.id == user_id).one_or_none()

    if not user:
        raise UserNotFound("User information not found")

    return user
