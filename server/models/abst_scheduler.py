from abc import ABCMeta, abstractmethod


class AbstScheduler(metaclass=ABCMeta):
    @abstractmethod
    def init_jobs(self):
        pass
