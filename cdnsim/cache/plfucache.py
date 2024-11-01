from .cache import Cache
from ..requests import Requests


class PLFUCache(Cache):
    def __init__(self, size: int, **kwargs):
        super().__init__(**kwargs)
        self._size = size

    def process_requests(self, requests: Requests) -> None:
        self.log(f"{self._rpt.iloc[-1]}rps")
        raise NotImplementedError("TODO: implement")
