from abc import abstractmethod, ABCMeta


class LogMixIn(metaclass=ABCMeta):
    INFO = 'INFO'

    @abstractmethod
    def log(self, buff: str, severity: str = INFO) -> None:
        ...
