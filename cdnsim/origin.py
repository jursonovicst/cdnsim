from cdnsim.requests import IngressMixIn
from cdnsim.requests import Requests
from nodes.log import LoggerMixIn, DummylogMixIn
from nodes.node import LNode


class Origin(LoggerMixIn, IngressMixIn, LNode):
    def _process_ingress(self, requests: Requests) -> None:
        self._log(f"{self._rpt.iloc[-1]}rps")
