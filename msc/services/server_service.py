from msc.models import Server
from msc import db

def get_servers():

    servers = db.session.query(Server).all()

    return servers