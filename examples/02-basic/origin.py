from typing import cast

from cdnsim.requests import BaseRequests
from nodes.log import LoggerMixIn
from nodes.node import LNode


class Origin(LoggerMixIn, LNode):
    """
    Simple origin implementation. Logs the number of requests received.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._requests = BaseRequests([], {'tick': [], 'content': []})

    def _work(self) -> None:
        while recv := self._receive():
            assert isinstance(recv, list) and len(recv) > 0, recv
            self._log(f"received {cast(BaseRequests, sum(recv)).sum()} requests")
