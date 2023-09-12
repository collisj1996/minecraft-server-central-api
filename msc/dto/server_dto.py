from typing import List, Optional
from uuid import UUID

from msc.dto.base import BaseDto
from msc.models import Server
from msc.constants import CDN_DOMAIN

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


class ServersGetOutputDto(BaseDto):
    __root__: List[ServerDto]


class ServerCreateInputDto(BaseDto):
    name: str
    description: Optional[str]
    ip_address: str
    port: Optional[int]
    country_code: str
    minecraft_version: str
    votifier_ip_address: Optional[str]
    votifier_port: Optional[int]
    votifier_key: Optional[str]
    website: Optional[str]
    discord: Optional[str]
    banner_base64: Optional[str]


class ServerUpdateInputDto(BaseDto):
    id: int
    name: str
    description: str
    ip_address: str
    port: int
