from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Server(Base):
    __tablename__ = 'server'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    ip_address = Column(String)
    port = Column(Integer)
    website = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)