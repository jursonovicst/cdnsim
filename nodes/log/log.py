from abc import abstractmethod, ABCMeta
from enum import Enum


class LogLevel(Enum):
    INFO = 1


class LogMixIn(metaclass=ABCMeta):
    INFO: LogLevel = LogLevel.INFO

    @classmethod
    @abstractmethod
    def setlevel(cls, loglevel: LogLevel) -> None:
        ...

    @abstractmethod
    def _log(self, buff: str, severity: str = INFO) -> None:
        ...

    @abstractmethod
    def _exception(self, buff: str) -> None:
        ...
