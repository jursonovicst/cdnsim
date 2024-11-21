from typing import cast

from cdnsim.cache import Cache
from cdnsim.requests import Requests


class NonCache(Cache):
    """
    For demonstration purposes, a non caching cache implementation.
    """

    def _work(self) -> None:
        while recv := self._receive():
            assert isinstance(recv, list) and len(recv) > 0, recv
            for remote, request in zip(self.remotes, cast(Requests, sum(recv)) // len(self.remotes)):
                self._send(remote, request)
        self._terminate()
