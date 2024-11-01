from abc import ABC, abstractmethod


class LogMixIn(ABC):
    @abstractmethod
    def _info(self, buff: str) -> None:
        ...
