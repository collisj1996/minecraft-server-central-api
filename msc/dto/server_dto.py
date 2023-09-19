from typing import List, Optional
from uuid import UUID

from msc.dto.custom_types import NOT_SET
from msc.dto.base import BaseDto
from msc.models import Server


class ServerDto(BaseDto):
    id: UUID
    name: str
    description: Optional[str]
    ip_address: str
    port: Optional[int]
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

    @classmethod
    def from_service(cls, server: Server):
        return cls(
            id=server.id,
            name=server.name,
            description=server.description,
            ip_address=server.ip_address,
            port=server.port,
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
            banner_url=server.banner_url,
        )


class GetServerDto(ServerDto):
    total_votes: int
    votes_this_month: int

    @classmethod
    def from_service(cls, service_output):
        return cls(
            id=service_output[0].id,
            name=service_output[0].name,
            description=service_output[0].description,
            ip_address=service_output[0].ip_address,
            port=service_output[0].port,
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
            banner_url=service_output[0].banner_url,
            total_votes=service_output[1],
            votes_this_month=service_output[2],
        )


class ServersGetOutputDto(BaseDto):
    __root__: List[GetServerDto]


class ServerCreateInputDto(BaseDto):
    name: str
    description: Optional[str] = None
    ip_address: str
    port: Optional[int] = None
    country_code: str
    minecraft_version: str
    votifier_ip_address: Optional[str] = None
    votifier_port: Optional[int] = None
    votifier_key: Optional[str] = None
    website: Optional[str] = None
    discord: Optional[str] = None
    banner_base64: Optional[str] = None


class ServerUpdateInputDto(BaseDto):
    name: Optional[str] = NOT_SET
    description: Optional[str] = NOT_SET
    ip_address: Optional[str] = NOT_SET
    port: Optional[int] = NOT_SET
    country_code: Optional[str] = NOT_SET
    minecraft_version: Optional[str] = NOT_SET
    votifier_ip_address: Optional[str] = NOT_SET
    votifier_port: Optional[int] = NOT_SET
    votifier_key: Optional[str] = NOT_SET
    website: Optional[str] = NOT_SET
    discord: Optional[str] = NOT_SET
    banner_base64: Optional[str] = NOT_SET


class ServerDeleteOutputDto(BaseDto):
    deleted_server_id: UUID
