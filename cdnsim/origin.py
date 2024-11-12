from cdnsim.requests import IngressMixIn
from cdnsim.requests import Requests
from nodes.log import LoggerMixIn, DummylogMixIn
from nodes.node import LNode


class Origin(LoggerMixIn, IngressMixIn, LNode):
    def process_requests(self, requests: Requests) -> None:
        self._log(f"{self._rpt.iloc[-1]}rps")
