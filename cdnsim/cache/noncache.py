from cdnsim.cache import Cache
from cdnsim.requests import Requests


class NonCache(Cache):

    def process_requests(self, requests: Requests) -> None:
        self.log(f"{self._rpt.iloc[-1]}rps")
        for remote in self.remotes:
            self._send(remote, requests / len(self.remotes))
