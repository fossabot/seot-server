import enum


class RequestStatus(enum.Enum):
    accept = 1
    stop = 2

    @classmethod
    def choice(cls):
        return [(m.value, m.name) for m in cls]
