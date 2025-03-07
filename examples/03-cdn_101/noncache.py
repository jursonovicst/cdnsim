from cdnsim.cache import Cache
from nodes.log import LogLevel
from throughput import ThroughputRequests


class NonCache(Cache):
    """
    For demonstration purposes, a non caching cache implementation.
    """

    def _work(self) -> None:
        # receive messages from all remotes until termination (empty list) received
        try:
            while (msgs := self._receive()) is not None:
                requests = ThroughputRequests.merge_requests(msgs)
                self._log(f"Received {requests.freq.sum()} requests", LogLevel.DEBUG)
                self._send(requests.split_rr(len(self.downstreams)))
        except Exception as e:
            self._exception()
