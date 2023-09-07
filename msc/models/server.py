from sqlalchemy import Column, Integer, String, DateTime

from msc import db


class Server(db.Base):
    """
    Represents a server listing
    """

    __tablename__ = "server"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    ip_address = Column(String)
    port = Column(Integer)
    website = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __init__(
        self,
        name,
        description,
        ip_address,
        port,
        website,
        created_at,
        updated_at,
    ):
        self.name = name
        self.description = description
        self.ip_address = ip_address
        self.port = port
        self.website = website
        self.created_at = created_at
        self.updated_at = updated_at
