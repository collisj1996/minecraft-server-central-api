from msc.dto.base import BaseDto
from msc.models import MinecraftVersion


class GetVersionsOutputDto(BaseDto):
    __root__: list[str]

    @classmethod
    def from_service(cls, versions: list[MinecraftVersion]):
        return cls(
            __root__=[v.version for v in versions],
        )
