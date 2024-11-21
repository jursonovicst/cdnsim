from cdnsim.cache.cache import Cache
from cdnsim.requests import BaseRequests


class PLFUCache(Cache):
    def __init__(self, size: int, **kwargs):
        super().__init__(**kwargs)
        self._size = size

    def process_requests(self, requests: BaseRequests) -> None:
        self._log(f"{self._rpt.iloc[-1]}rps")
        raise NotImplementedError("TODO: implement")
