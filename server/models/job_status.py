import enum


class JobStatus(enum.Enum):
    idle = 1
    accept_pending = 2
    running = 3
    stop_pending = 4

    @classmethod
    def choices(cls):
        return [(m.value, m.name) for m in cls]
