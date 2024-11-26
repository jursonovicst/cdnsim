from nodes.log import LogMixIn, LoggerMixIn

# Create a simple CDN setup consisting of two clients, two caches and a single origin.
#
# [client1] -┐┌-> [cache1] -┐
#            ├┤             ├-> [cache3] --> [origin]
# [client2] -┘└-> [cache2] -┘
#
# the clients are requesting different profiles of Zipf distribution according to different arrival processes, the
# caches are NonCaches, meaning, they do not cache at all (just for this example), and the origin is a simple origin.

LoggerMixIn.setlevel(LogMixIn.INFO)

# the poisson arrival process implementation
from cdnsim.arrival import Arrival
from numpy.random import default_rng


class Poisson(Arrival):
    def __init__(self, lam: float, **kwargs):
        super().__init__(**kwargs)
        if lam <= 1:
            raise ValueError(f"lambda for poisson should be greater or equal to 1, got: {lam}")
        self.__lam = lam
        self.__rng = default_rng()

    def __next__(self) -> int:
        super().__next__()
        return int(self.__rng.poisson(self.__lam, 1)[0])


# the zipf client implementation
from zipf import ZipfClient

# PLFU cache implementation
from plfucache import PLFUCache

# origin implementation
from cdnsim import Origin
from throughput import ThroughputRequests


class MyOrigin(Origin):

    def _work(self) -> None:
        while (msgs := self._receive()) is not None:
            self._log(f"received {ThroughputRequests.merge_requests(msgs).freq.sum()} requests")


if __name__ == "__main__":

    # create client
    client1 = ZipfClient(name='client1', cbase=20, n=50, p=0.5, a=1.6, arrival=Poisson(lam=50, ticks=10))
    client2 = ZipfClient(name='client2', cbase=100, n=200, p=0.3, a=1.1, arrival=Poisson(lam=80, ticks=10))

    # create caches
    cache1 = PLFUCache(name='cache1', size=200)
    cache2 = PLFUCache(name='cache2', size=200)
    cache3 = PLFUCache(name='cache3', size=400)

    # create origin
    origin = MyOrigin(name='origin')

    # establish connections
    client1.connect_to(cache1)
    client1.connect_to(cache2)
    client2.connect_to(cache1)
    client2.connect_to(cache2)
    cache1.connect_to(cache3)
    cache2.connect_to(cache3)
    cache3.connect_to(origin)

    # run simulation
    try:
        client1.start_all()
        client1.join_all()
    except KeyboardInterrupt:
        pass
    finally:
        client1.terminate_all()
