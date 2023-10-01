from datetime import datetime

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
