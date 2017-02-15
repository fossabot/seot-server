import enum


class AppStatus(enum.Enum):
    idle = 1
    launching = 2
    running = 3
    stopping = 4

    @classmethod
    def choices(cls):
        return [(m.value, m.name) for m in cls]
