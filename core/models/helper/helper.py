from enum import Enum


class EnumField(Enum):
    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)

    def __str__(self):
        return str(self.value)
