from msc.dto.base import BaseDto


class GetTagsOutputDto(BaseDto):
    __root__: list[str]
