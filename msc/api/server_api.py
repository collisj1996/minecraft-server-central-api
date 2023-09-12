from fastapi import APIRouter

from msc.dto.server_dto import ServerCreateInputDto, ServerDto, ServersGetOutputDto
from msc.services import server_service

router = APIRouter()


@router.get("/health")
def health():
    return {"message": "healthy"}


@router.post("/servers")
def create_server(body: ServerCreateInputDto):
    """Endpoint for creating a server"""

    # TODO: Add authentication here?

    server = server_service.create_server(
        name=body.name,
        description=body.description,
        ip_address=body.ip_address,
        port=body.port,
        country_code=body.country_code,
        minecraft_version=body.minecraft_version,
        votifier_ip_address=body.votifier_ip_address,
        votifier_port=body.votifier_port,
        votifier_key=body.votifier_key,
        website=body.website,
        discord=body.discord,
        banner_base64=body.banner_base64,
    )

    return ServerDto.from_service(server)


@router.put("/servers")
def update_server(server):
    """Endpoint for updating a server"""

    # TODO: Add authentication here?

    return server_service.update_server(server)


@router.get("/servers")
def get_servers():
    """Endpoint for getting all servers"""

    servers = server_service.get_servers()

    dto = ServersGetOutputDto(__root__=[ServerDto.from_service(s) for s in servers])

    return dto
