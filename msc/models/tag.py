from uuid import uuid4

from sqlalchemy import Column, ForeignKeyConstraint, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from msc.database import Base


class Tag(Base):
    """
    Represents a server tag
    """

    __tablename__ = "tag"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4)
    server_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "id",
            name="unique_tag_id",
        ),
        ForeignKeyConstraint(
            ["server_id"],
            ["server.id"],
            ondelete="CASCADE",
        ),
    )

    def __init__(
        self,
        server_id,
        name,
    ):
        self.server_id = server_id
        self.name = name
