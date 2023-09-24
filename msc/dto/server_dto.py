from typing import List, Optional
from uuid import UUID
from pydantic import conint, validator, conlist

from msc.constants import ALLOWED_GAMEPLAY, CDN_DOMAIN
from msc.dto.custom_types import NOT_SET
from msc.dto.base import BaseDto
from msc.models import Server


def _get_server_icon_url(
    server: Server,
) -> Optional[str]:
    return (
        f"https://{CDN_DOMAIN}/icon/{server.id}.png" if server.icon_checksum else None
    )


def _get_server_banner_url(
    server: Server,
) -> Optional[str]:
    return (
        f"https://{CDN_DOMAIN}/banner/{server.id}.{server.banner_filetype}"
        if server.banner_checksum
        else None
    )


class ServerDto(BaseDto):
    id: UUID
    name: str
    description: Optional[str]
    java_ip_address: Optional[str]
    bedrock_ip_address: Optional[str]
    java_port: Optional[int]
    bedrock_port: Optional[int]
    players: int
    max_players: int
    is_online: bool
    country_code: str
    minecraft_version: str
    votifier_ip_address: Optional[str]
    votifier_port: Optional[int]
    votifier_key: Optional[str]
    website: Optional[str]
    discord: Optional[str]
    banner_url: Optional[str]
    icon_url: Optional[str]
    gameplay: List[str]

    @classmethod
    def from_service(cls, server: Server):
        return cls(
            id=server.id,
            name=server.name,
            description=server.description,
            java_ip_address=server.java_ip_address,
            bedrock_ip_address=server.bedrock_ip_address,
            java_port=server.java_port,
            bedrock_port=server.bedrock_port,
            players=server.players,
            max_players=server.max_players,
            is_online=server.is_online,
            country_code=server.country_code,
            minecraft_version=server.minecraft_version,
            votifier_ip_address=server.votifier_ip_address,
            votifier_port=server.votifier_port,
            votifier_key=server.votifier_key,
            website=server.website,
            discord=server.discord,
            banner_url=_get_server_banner_url(server),
            icon_url=_get_server_icon_url(server),
            gameplay=[g.name for g in server.gameplay],
        )


class ServersGetInputDto(BaseDto):
    page: Optional[conint(ge=1)] = 1
    page_size: Optional[conint(ge=10, le=30)] = 10
    filter: Optional[str] = None


class GetServerDto(ServerDto):
    rank: int
    total_votes: int
    votes_this_month: int

    @classmethod
    def from_service(cls, service_output):
        return cls(
            id=service_output[0].id,
            name=service_output[0].name,
            description=service_output[0].description,
            java_ip_address=service_output[0].java_ip_address,
            bedrock_ip_address=service_output[0].bedrock_ip_address,
            java_port=service_output[0].java_port,
            bedrock_port=service_output[0].bedrock_port,
            players=service_output[0].players,
            max_players=service_output[0].max_players,
            is_online=service_output[0].is_online,
            country_code=service_output[0].country_code,
            minecraft_version=service_output[0].minecraft_version,
            votifier_ip_address=service_output[0].votifier_ip_address,
            votifier_port=service_output[0].votifier_port,
            votifier_key=service_output[0].votifier_key,
            website=service_output[0].website,
            discord=service_output[0].discord,
            banner_url=_get_server_banner_url(service_output[0]),
            icon_url=_get_server_icon_url(service_output[0]),
            gameplay=[g.name for g in service_output[0].gameplay],
            rank=service_output[3],
            total_votes=service_output[1],
            votes_this_month=service_output[2],
        )


class ServersGetOutputDto(BaseDto):
    total_servers: int
    servers: List[GetServerDto]


class ServersMineOutputDto(BaseDto):
    __root__: List[GetServerDto]


class ServerCreateInputDto(BaseDto):
    name: str
    description: Optional[str] = None
    java_ip_address: Optional[str] = None
    bedrock_ip_address: Optional[str] = None
    java_port: Optional[int] = None
    bedrock_port: Optional[int] = None
    country_code: str
    minecraft_version: str
    votifier_ip_address: Optional[str] = None
    votifier_port: Optional[int] = None
    votifier_key: Optional[str] = None
    website: Optional[str] = None
    discord: Optional[str] = None
    banner_base64: Optional[str] = None
    gameplay: conlist(str, min_items=3, max_items=10)

    @validator("bedrock_ip_address")
    def validate_ip_addresses(cls, ip_address, values):
        # TODO: Add test for this
        if "java_ip_address" not in values and not ip_address:
            raise ValueError(
                "At least one of java_ip_address or bedrock_ip_address must be set"
            )

        return ip_address

    @validator("gameplay")
    def validate_gameplay(cls, gameplay):
        for g in gameplay:
            if g not in ALLOWED_GAMEPLAY:
                raise ValueError(
                    f"Invalid gameplay: {g}. Allowed gameplay: {ALLOWED_GAMEPLAY}"
                )
        return gameplay


class ServerUpdateInputDto(BaseDto):
    name: Optional[str] = NOT_SET
    description: Optional[str] = NOT_SET
    java_ip_address: Optional[str] = NOT_SET
    bedrock_ip_address: Optional[str] = NOT_SET
    java_port: Optional[int] = NOT_SET
    bedrock_port: Optional[int] = NOT_SET
    country_code: Optional[str] = NOT_SET
    minecraft_version: Optional[str] = NOT_SET
    votifier_ip_address: Optional[str] = NOT_SET
    votifier_port: Optional[int] = NOT_SET
    votifier_key: Optional[str] = NOT_SET
    website: Optional[str] = NOT_SET
    discord: Optional[str] = NOT_SET
    banner_base64: Optional[str] = NOT_SET
    gameplay: Optional[conlist(str, min_items=3, max_items=10)] = NOT_SET

    @validator("bedrock_ip_address")
    def validate_ip_addresses(cls, ip_address, values):
        # TODO: Add test for this
        if "java_ip_address" not in values and not ip_address:
            raise ValueError(
                "At least one of java_ip_address or bedrock_ip_address must be set"
            )

        return ip_address

    @validator("gameplay")
    def validate_gameplay(cls, gameplay):
        for g in gameplay:
            if g not in ALLOWED_GAMEPLAY:
                raise ValueError(
                    f"Invalid gameplay: {g}. Allowed gameplay: {ALLOWED_GAMEPLAY}"
                )
        return gameplay


class ServerDeleteOutputDto(BaseDto):
    deleted_server_id: UUID
