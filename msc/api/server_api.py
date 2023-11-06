from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.requests import Request
from sqlalchemy.orm import Session

from msc.database import get_db
from msc.dto.server_dto import (
    GetServerDto,
    ServerCreateInputDto,
    ServerDeleteOutputDto,
    ServerDto,
    ServerGetHistoryInputDto,
    ServerGetInputDto,
    ServerHistoryDto,
    ServerPingOutputDto,
    ServersGetInputDto,
    ServersGetOutputDto,
    ServersMineGetInputDto,
    ServersMineOutputDto,
    ServersSponsoredGetOutputDto,
    ServerTestVotifierInputDto,
    ServerUpdateInputDto,
)
from msc.services import ping_service, server_service, vote_service
from msc.utils import api_utils
from msc.utils.api_utils import auth_required

router = APIRouter()


@router.post("/servers")
@auth_required
def create_server(
    request: Request,
    body: ServerCreateInputDto,
    db: Session = Depends(get_db),
) -> ServerDto:
    """Endpoint for creating a server"""

    user_id = request.state.user_id

    server = server_service.create_server(
        db=db,
        name=body.name,
        user_id=user_id,
        description=body.description,
        java_ip_address=body.java_ip_address,
        bedrock_ip_address=body.bedrock_ip_address,
        java_port=body.java_port,
        bedrock_port=body.bedrock_port,
        country_code=body.country_code,
        use_votifier=body.use_votifier,
        votifier_ip_address=body.votifier_ip_address,
        votifier_port=body.votifier_port,
        votifier_key=body.votifier_key,
        website=body.website,
        discord=body.discord,
        banner_base64=body.banner_base64,
        tags=body.tags,
        video_url=body.video_url,
        web_store=body.web_store,
        owner_name=body.owner_name,
    )

    return ServerDto.from_service(server)


@router.get("/servers/mine")
@auth_required
def get_my_servers(
    request: Request,
    query_params: ServersMineGetInputDto = Depends(),
    db: Session = Depends(get_db),
) -> ServersMineOutputDto:
    """Endpoint for getting all servers"""

    user_id = request.state.user_id

    my_servers = server_service.get_my_servers(
        db=db,
        user_id=user_id,
        include_auction_eligibility=query_params.include_auction_eligibility,
    )

    dto = ServersMineOutputDto(
        __root__=[GetServerDto.from_service(s) for s in my_servers],
    )

    return dto


@router.get("/servers/sponsored")
def get_sponsored_servers(
    db: Session = Depends(get_db),
) -> ServersSponsoredGetOutputDto:
    """Endpoint for getting all currently sponsored servers"""

    sponsored_servers = server_service.get_sponsored_servers(db=db)

    return ServersSponsoredGetOutputDto(
        __root__=[GetServerDto.from_service(s) for s in sponsored_servers]
    )


@router.get("/servers/{server_id}")
def get_server(
    server_id: str,
    query_params: ServerGetInputDto = Depends(),
    db: Session = Depends(get_db),
) -> GetServerDto:
    """Endpoint for getting a server"""

    server = server_service.get_server(
        db=db,
        server_id=server_id,
        include_auction_eligibility=query_params.include_auction_eligibility,
    )

    return GetServerDto.from_service(server)


@router.get("/servers")
def get_servers(
    query_params: ServersGetInputDto = Depends(),
    db: Session = Depends(get_db),
) -> ServersGetOutputDto:
    """Endpoint for getting all servers"""

    get_servers_info = server_service.get_servers(
        db=db,
        page=query_params.page,
        page_size=query_params.page_size,
        search_query=query_params.search_query,
        country_code=query_params.country_code,
        tags=query_params.tags,
        versions=query_params.versions,
    )

    dto = ServersGetOutputDto(
        total_servers=get_servers_info.total_servers,
        servers=[GetServerDto.from_service(s) for s in get_servers_info.servers],
    )

    return dto


@router.patch("/servers/{server_id}")
@auth_required
def update_server(
    request: Request,
    server_id: str,
    body: ServerUpdateInputDto,
    db: Session = Depends(get_db),
) -> ServerDto:
    """Endpoint for updating a server"""

    user_id = request.state.user_id

    server = server_service.update_server(
        db=db,
        server_id=UUID(server_id),
        name=body.name,
        user_id=UUID(user_id),
        description=body.description,
        java_ip_address=body.java_ip_address,
        bedrock_ip_address=body.bedrock_ip_address,
        java_port=body.java_port,
        bedrock_port=body.bedrock_port,
        country_code=body.country_code,
        use_votifier=body.use_votifier,
        votifier_ip_address=body.votifier_ip_address,
        votifier_port=body.votifier_port,
        votifier_key=body.votifier_key,
        website=body.website,
        discord=body.discord,
        banner_base64=body.banner_base64,
        tags=body.tags,
        video_url=body.video_url,
        web_store=body.web_store,
        owner_name=body.owner_name,
    )

    return ServerDto.from_service(server)


@router.delete("/servers/{server_id}")
@auth_required
def delete_server(
    request: Request,
    server_id: str,
    db: Session = Depends(get_db),
) -> ServerDeleteOutputDto:
    """Endpoint for deleting a server"""

    user_id = request.state.user_id

    deleted_server_id = server_service.delete_server(
        db=db,
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
    db: Session = Depends(get_db),
) -> ServerPingOutputDto:
    """Endpoint for pinging a server"""

    user_id = request.state.user_id

    response = ping_service.poll_server_by_id(
        db=db,
        server_id=UUID(server_id),
        user_id=UUID(user_id),
    )

    return ServerPingOutputDto(
        message=response,
    )


@router.get("/servers/{server_id}/historical")
def get_server_historical_data(
    server_id: str,
    query_params: ServerGetHistoryInputDto = Depends(),
    db: Session = Depends(get_db),
) -> list[ServerHistoryDto]:
    """Endpoint for getting a server's historical data"""

    server_history = server_service.get_server_history(
        db=db,
        server_id=UUID(server_id),
        time_interval=query_params.time_interval,
    )

    return [ServerHistoryDto.from_service(s) for s in server_history]


@router.post("/servers/{server_id}/test_votifier")
@auth_required
def test_votifier(
    request: Request,
    server_id: str,
    body: ServerTestVotifierInputDto,
    db: Session = Depends(get_db),
) -> ServerPingOutputDto:
    """Endpoint for testing votifier"""

    client_ip = api_utils.get_client_ip(request)

    user_id = request.state.user_id

    response = vote_service.test_votifier(
        db=db,
        server_id=UUID(server_id),
        user_id=UUID(user_id),
        client_ip=client_ip,
        minecraft_username=body.minecraft_username,
    )

    return {
        "message": "ok",
    }
