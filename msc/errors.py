"""Defines custom errors for the msc package."""
import re
from uuid import UUID

from msc.dto.util import ErrorOutputDto


class ApplicationError(Exception):
    """Base class for all application errors."""

    def __init__(
        self,
        message: str,
        *,
        user_id: UUID = None,
    ):
        """Initialize the error with a message."""
        self.message = message
        self.user_id = user_id

        try:
            self.get_http_status_code()
        except TypeError:
            raise TypeError(
                "ApplicationError subclasses must define a get_http_status_code method."
            )

    def to_dto(self) -> ErrorOutputDto:
        """Return a DTO representation of the error."""
        return ErrorOutputDto(
            type=self.get_type(),
            message=self.message,
            data=self.get_data(),
        )

    def to_json(self) -> dict:
        """Return a JSON representation of the error."""
        return self.to_dto().dict()

    def get_type(self) -> str:
        """Return the type of error."""
        return re.sub(r"(?<!^)(?=[A-Z])", "_", self.__class__.__name__).lower()

    def get_data(self) -> dict:
        """Return data about the error to be encoded into the JSON response."""
        data = {}

        if self.user_id:
            data["user_id"] = str(self.user_id)

        return data

    def get_http_status_code(self) -> int:
        """Return the HTTP status code to be used in the response."""
        raise TypeError("get_http_status_code not implemented")


class BadRequest(ApplicationError):
    """Represents a 400 Bad Request error."""

    def get_http_status_code(self) -> int:
        """Return the HTTP status code to be used in the response."""
        return 400


class Unauthorized(ApplicationError):
    """Represents a 401 Unauthorized error."""

    def get_http_status_code(self) -> int:
        """Return the HTTP status code to be used in the response."""
        return 401


class Forbidden(ApplicationError):
    """Represents a 403 Forbidden error."""

    def get_http_status_code(self) -> int:
        """Return the HTTP status code to be used in the response."""
        return 403


class NotFound(ApplicationError):
    """Represents a 404 Not Found error."""

    def get_http_status_code(self) -> int:
        """Return the HTTP status code to be used in the response."""
        return 404


class InternalError(ApplicationError):
    """Represents a 500 Internal Server Error error."""

    def get_http_status_code(self) -> int:
        """Return the HTTP status code to be used in the response."""
        return 500


class TooManyRequests(ApplicationError):
    """Represents a 429 Too Many Requests error."""

    def get_http_status_code(self) -> int:
        """Return the HTTP status code to be used in the response."""
        return 429
