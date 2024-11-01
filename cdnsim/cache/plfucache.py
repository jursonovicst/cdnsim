from .cache import Cache


class PLFUCache(Cache):
    def __init__(self, size: int, **kwargs):
        super().__init__(**kwargs)
        self._size = size

    def work(self) -> None:
        pass
