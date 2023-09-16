from fastapi import APIRouter
from fastapi.requests import Request

from msc.dto.server_dto import (
    ServerCreateInputDto,
    ServerDto,
    ServersGetOutputDto,
    GetServersDto,
)
from msc.services import server_service

router = APIRouter()


@router.post("/servers")
def create_server(request: Request, body: ServerCreateInputDto):
    """Endpoint for creating a server"""

    # TODO: Add authentication here?
    user_id = request.state.user_id

    server = server_service.create_server(
        name=body.name,
        user_id=user_id,
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



@router.get("/servers/{server_id}")
def get_server(server_id: str):
    """Endpoint for getting a server"""

    server = server_service.get_server(server_id)

    return ServerDto.from_service(server)


@router.get("/servers")
def get_servers():
    """Endpoint for getting all servers"""

    servers_resp = server_service.get_servers()

    dto = ServersGetOutputDto(
        __root__=[GetServersDto.from_service(s) for s in servers_resp]
    )

    return dto


@router.patch("/servers/{server_id}")
def update_server(server_id: str, server: ServerDto):
    """Endpoint for updating a server"""

    # TODO: Add authentication here?

    return server_service.update_server(server)


@router.delete("/servers/{server_id}")
def delete_server(server_id: str):
    """Endpoint for deleting a server"""