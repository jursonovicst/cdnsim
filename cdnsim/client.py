from abc import ABC, abstractmethod

from cdnsim.requests import BaseRequests
from nodes.log import LoggerMixIn
from nodes.node import TNode
from typing import Iterator, List, Tuple

class Client(LoggerMixIn, TNode, ABC):

    def _work(self, *args) -> None:
        for requests in self._generate():
            for remote, request in requests:
                self._send(remote, request)  # <-- evenly distributed among nodes
        self._terminate()

    @abstractmethod
    def _generate(self) -> Iterator[List[Tuple[str, BaseRequests]]]:
        ...
