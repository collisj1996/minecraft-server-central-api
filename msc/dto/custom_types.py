from datetime import datetime

from msc.constants import QUERY_STRING_TAG_LIST_MAX, QUERY_STRING_VERSION_LIST_MAX
from msc.dto.base import BaseDto


class NotSet(BaseDto):
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return True


NOT_SET = NotSet()


class DateTimeUTC(datetime):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if value is not None and isinstance(value, datetime):
            return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            return value


class DateTimeIsoStr(datetime):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        return value


class TagsCommaSeperatedStringToList(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        tag_list = []
        if isinstance(value, str):
            tag_list = value.split(",")
            if len(tag_list) > QUERY_STRING_TAG_LIST_MAX:
                raise ValueError(
                    f"Tag list cannot be longer than {QUERY_STRING_TAG_LIST_MAX}"
                )
        else:
            return value
        return tag_list


class VersionsCommaSeperatedStringToList(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        version_list = []
        if isinstance(value, str):
            version_list = value.split(",")
            if len(version_list) > QUERY_STRING_VERSION_LIST_MAX:
                raise ValueError(
                    f"Version list cannot be longer than {QUERY_STRING_VERSION_LIST_MAX}"
                )
        else:
            return value
        return version_list
