from pydantic import BaseModel


class ErrorOutputDto(BaseModel):
    """Represents an error that can be returned to the client."""

    type: str = "unhandled_error"
    message: str
    data: dict = {}
