from abc import ABC, abstractmethod

from cdnsim.content import Obj


class LogMixIn(ABC):
    @abstractmethod
    def _info(self, buff: str) -> None:
        ...

    @abstractmethod
    def _request(self, tick: int, obj: Obj) -> None:
        ...
