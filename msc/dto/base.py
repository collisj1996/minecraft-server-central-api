from pydantic import BaseModel, Extra


class BaseDto(BaseModel):
    """DTO that all other DTOs inherit from. This is to ensure that all DTOs have the same configuration."""

    class Config:
        extra = Extra.forbid
