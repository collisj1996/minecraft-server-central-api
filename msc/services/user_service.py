from contextlib import contextmanager
from uuid import UUID
import boto3

from sqlalchemy.orm import Session

from msc.models import User
from msc.errors import NotFound, BadRequest, Unauthorized, InternalError


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


def change_password(
    token: str,
    current_password: str,
    new_password: str,
):
    """Sends a request to AWS to change a Cognito identity password"""

    cognito_client = boto3.client("cognito-idp")

    try:
        response = cognito_client.change_password(
            PreviousPassword=current_password,
            ProposedPassword=new_password,
            AccessToken=token,
        )
    except cognito_client.exceptions.ResourceNotFoundException:
        raise BadRequest(
            message="Resource not found",
        )
    except cognito_client.exceptions.InvalidParameterException:
        raise BadRequest(
            message="Invalid parameter",
        )
    except cognito_client.exceptions.InvalidPasswordException:
        raise BadRequest(
            message="Invalid password",
        )
    except cognito_client.exceptions.NotAuthorizedException:
        raise BadRequest(
            message="Invalid password",
        )
    except Exception as err:
        raise InternalError(message=str(err))
