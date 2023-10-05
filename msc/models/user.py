from datetime import datetime

from sqlalchemy import Column, DateTime, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from msc.database import Base


class User(Base):
    """
    Represents a user
    """

    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    username = Column(Text, nullable=False)
    email = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "id",
            name="unique_user_id",
        ),
    )

    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

        now = datetime.utcnow()
        self.created_at = now
        self.updated_at = now
