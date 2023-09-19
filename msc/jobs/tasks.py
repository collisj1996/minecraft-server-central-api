import logging

from msc import db
from msc.models import Server
from mcstatus import JavaServer, BedrockServer

logger = logging.getLogger(__name__)


def poll_servers():
    """Polls minecraft servers for information"""

    # Get all servers
    servers = db.session.query(Server).all()

    for server in servers:
        # TODO: account for timeouts and errors, fail gracefully

        logger.info("Polling server: %s", server.ip_address)

        ip = server.ip_address

        if server.port:
            ip = f"{ip}:{server.port}"

        server = JavaServer.lookup(ip)

        try:
            status = server.status()
            logger.info("Server status: %s", status)
            logger.info(f"Server replied in {status.latency} ms")
        except Exception as e:
            logger.error("Error getting server status: %s", e)
            continue

        try:
            query = server.query()
            logger.info("Server query: %s", query)
        except Exception as e:
            logger.error("Error getting server query: %s", e)
            continue
