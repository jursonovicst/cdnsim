from cdnsim.cache import Cache
from cdnsim.requests import Requests


class NonCache(Cache):
    """
    For demonstration purposes, a non caching cache implementation.
    """
    def _process_ingress(self, requests: Requests) -> None:
        # do not cache, simply forward all requests via a round-robin remote selection
        for remote, request in zip(self.remotes, requests / len(self.remotes)):
            self._send(remote, request)
