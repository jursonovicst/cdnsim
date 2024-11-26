from cdnsim.cache import Cache
from throughput import ThroughputRequests


class PLFUCache(Cache):
    def __init__(self, size: int, **kwargs):
        super().__init__(**kwargs)
        self._size = size

    def _work(self) -> None:
        try:
            while (msgs := self._receive()) is not None:
                rank = ThroughputRequests.merge_requests(msgs).sort_values('freq', ascending=False)
                rank['volume'] = rank['size'].cumsum()
                rank.loc[rank['volume'] < self._size, 'freq'] = 1
                msg = ThroughputRequests(rank[['freq', 'size']])
                assert isinstance(msg, ThroughputRequests), f"{type(msg)}, {msg}"
                self._send(msg.split_rr(len(self.remotes)))
        except Exception as e:
            self._exception()
