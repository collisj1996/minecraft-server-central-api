from fastapi import APIRouter, Depends
from fastapi.requests import Request
from uuid import UUID

from msc.dto.server_dto import (
    GetServerDto,
    ServerCreateInputDto,
    ServerDto,
    ServersGetOutputDto,
    ServerUpdateInputDto,
    ServerDeleteOutputDto,
    ServersGetInputDto,
)
from msc.services import server_service

router = APIRouter()


@router.post("/servers")
def create_server(
    request: Request,
    body: ServerCreateInputDto,
) -> ServerDto:
    """Endpoint for creating a server"""

    user_id = request.state.user_id

    # TODO: Add authentication here

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
def get_server(server_id: str) -> GetServerDto:
    """Endpoint for getting a server"""

    server = server_service.get_server(server_id)

    return GetServerDto.from_service(server)


@router.get("/servers")
def get_servers(
    query_params: ServersGetInputDto = Depends(),
) -> ServersGetOutputDto:
    """Endpoint for getting all servers"""

    servers_resp, total_servers = server_service.get_servers(
        page=query_params.page,
        page_size=query_params.page_size,
        filter=query_params.filter,
    )

    dto = ServersGetOutputDto(
        total_servers=total_servers,
        servers=[GetServerDto.from_service(s) for s in servers_resp],
    )

    return dto


@router.patch("/servers/{server_id}")
def update_server(
    request: Request,
    server_id: str,
    body: ServerUpdateInputDto,
) -> ServerDto:
    """Endpoint for updating a server"""

    user_id = request.state.user_id

    # TODO: Add authentication here

    server = server_service.update_server(
        server_id=UUID(server_id),
        name=body.name,
        user_id=UUID(user_id),
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


@router.delete("/servers/{server_id}")
def delete_server(
    request: Request,
    server_id: str,
) -> ServerDeleteOutputDto:
    """Endpoint for deleting a server"""

    user_id = request.state.user_id

    # TODO: Add authentication here

    deleted_server_id = server_service.delete_server(
        server_id=UUID(server_id),
        user_id=UUID(user_id),
    )

    return ServerDeleteOutputDto(
        deleted_server_id=deleted_server_id,
    )
