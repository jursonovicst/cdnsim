from abc import ABC, abstractmethod


class LogMixIn(ABC):
    INFO = 'INFO'

    @abstractmethod
    def log(self, buff: str, severity: str = INFO) -> None:
        ...
