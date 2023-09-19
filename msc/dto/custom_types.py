from msc.dto.base import BaseDto


class NotSet(BaseDto):
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return True


NOT_SET = NotSet()
