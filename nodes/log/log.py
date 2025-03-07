from abc import abstractmethod, ABCMeta
from enum import Enum


class LogLevel(Enum):
    ERROR = 0
    WARNING = 1
    INFO = 2
    DEBUG = 3


class LogMixIn(metaclass=ABCMeta):
    ERROR: LogLevel = LogLevel.ERROR
    WARNING: LogLevel = LogLevel.WARNING
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
    def _exception(self, buff: str = "Unexpected exception") -> None:
        ...
