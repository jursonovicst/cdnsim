from cdnsim.requests import RequestMixIn
from cdnsim.requests import Requests
from framework.log import LoggerMixIn, DummylogMixIn
from framework.node import LNode


class Origin(LoggerMixIn, RequestMixIn, LNode):
    def process_requests(self, requests: Requests) -> None:
        self.log(f"{self._rpt.iloc[-1]}rps")
