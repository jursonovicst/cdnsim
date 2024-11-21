from abc import abstractmethod, ABCMeta
from enum import Enum


class LogLevel(Enum):
    INFO = 1
    DEBUG = 2


class LogMixIn(metaclass=ABCMeta):
    INFO: LogLevel = LogLevel.INFO
    DEBUG: LogLevel = LogLevel.DEBUG

    @classmethod
    @abstractmethod
    def setlevel(cls, loglevel: LogLevel) -> None:
        ...

    @abstractmethod
    def _log(self, buff: str, severity: LogLevel = INFO) -> None:
        ...

    @abstractmethod
    def _exception(self, buff: str) -> None:
        ...
