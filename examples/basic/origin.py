from typing import cast

from cdnsim.requests import Requests
from nodes.log import LoggerMixIn
from nodes.node import LNode


class Origin(LoggerMixIn, LNode):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._requests = Requests([], {'tick': [], 'content': []})

    def _work(self) -> None:
        while recv := self._receive():
            assert isinstance(recv, list) and len(recv) > 0, recv
            self._log(f"received {cast(Requests, sum(recv)).sum()} requests")
