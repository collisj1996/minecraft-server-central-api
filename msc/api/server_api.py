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
    ServersMineOutputDto,
    ServerPingOutputDto,
)
from msc.services import server_service, ping_service
from msc.utils.api_utils import auth_required

router = APIRouter()


@router.post("/servers")
@auth_required
def create_server(
    request: Request,
    body: ServerCreateInputDto,
) -> ServerDto:
    """Endpoint for creating a server"""

    user_id = request.state.user_id

    server = server_service.create_server(
        name=body.name,
        user_id=user_id,
        description=body.description,
        java_ip_address=body.java_ip_address,
        bedrock_ip_address=body.bedrock_ip_address,
        java_port=body.java_port,
        bedrock_port=body.bedrock_port,
        country_code=body.country_code,
        minecraft_version=body.minecraft_version,
        votifier_ip_address=body.votifier_ip_address,
        votifier_port=body.votifier_port,
        votifier_key=body.votifier_key,
        website=body.website,
        discord=body.discord,
        banner_base64=body.banner_base64,
        gameplay=body.gameplay,
    )

    return ServerDto.from_service(server)


@router.get("/servers/mine")
@auth_required
def get_my_servers(
    request: Request,
) -> ServersMineOutputDto:
    """Endpoint for getting all servers"""

    user_id = request.state.user_id

    my_servers = server_service.get_my_servers(user_id)

    dto = ServersMineOutputDto(
        __root__=[GetServerDto.from_service(s) for s in my_servers],
    )

    return dto


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
@auth_required
def update_server(
    request: Request,
    server_id: str,
    body: ServerUpdateInputDto,
) -> ServerDto:
    """Endpoint for updating a server"""

    user_id = request.state.user_id

    server = server_service.update_server(
        server_id=UUID(server_id),
        name=body.name,
        user_id=UUID(user_id),
        description=body.description,
        java_ip_address=body.java_ip_address,
        bedrock_ip_address=body.bedrock_ip_address,
        java_port=body.java_port,
        bedrock_port=body.bedrock_port,
        country_code=body.country_code,
        minecraft_version=body.minecraft_version,
        votifier_ip_address=body.votifier_ip_address,
        votifier_port=body.votifier_port,
        votifier_key=body.votifier_key,
        website=body.website,
        discord=body.discord,
        banner_base64=body.banner_base64,
        gameplay=body.gameplay,
    )

    return ServerDto.from_service(server)


@router.delete("/servers/{server_id}")
@auth_required
def delete_server(
    request: Request,
    server_id: str,
) -> ServerDeleteOutputDto:
    """Endpoint for deleting a server"""

    user_id = request.state.user_id

    deleted_server_id = server_service.delete_server(
        server_id=UUID(server_id),
        user_id=UUID(user_id),
    )

    return ServerDeleteOutputDto(
        deleted_server_id=deleted_server_id,
    )


@router.post("/servers/{server_id}/ping")
@auth_required
def ping_server(
    request: Request,
    server_id: str,
) -> ServerPingOutputDto:
    """Endpoint for pinging a server"""

    user_id = request.state.user_id

    response = ping_service.poll_server_by_id(
        server_id=UUID(server_id),
        user_id=UUID(user_id),
    )

    return ServerPingOutputDto(
        message=response,
    )
