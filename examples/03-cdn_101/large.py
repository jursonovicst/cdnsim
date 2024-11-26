from nodes.log import LogMixIn, LoggerMixIn

# Create a big CDN setup consisting of three tiers
#
# first tier:  24 pops, 30 servers each pop
# second tier: 24 pops, 4 servers each pop
# third tier: 1 pop, 30 servers
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


# extend the BaseRequests to track tick and content sizes
from zipf import ZipfClient

# noncache implementation
from noncache import NonCache

# origin implementation
from cdnsim import Origin
from throughput import ThroughputRequests


class MyOrigin(Origin):

    def _work(self) -> None:
        while (msgs := self._receive()) is not None:
            self._log(f"received {ThroughputRequests.merge_requests(msgs).freq.sum()} requests")


if __name__ == "__main__":

    npops = 10
    ndeliverers = 10
    nfetchers = 2
    nacquirers = 10

    # 1 origin
    origin = MyOrigin()

    # 30 content acquirers
    l3caches = []
    for i in range(nacquirers):
        c = NonCache(name=f"cache_l3_no{i}")
        c.connect_to(origin)
        l3caches.append(c)

    # 24 pops, 4 fetchers and 24 deliverers and a single client per pop
    pops = []
    for pop in range(npops):
        l2caches = []
        for i in range(nfetchers):
            c = NonCache(name=f"cache_l2_pop{pop}_no{i}")
            for l3 in l3caches:
                c.connect_to(l3)
            l2caches.append(c)

        l1caches = []
        for i in range(ndeliverers):
            c = NonCache(name=f"cache_l1_pop{pop}_no{i}")
            for l2 in l2caches:
                c.connect_to(l2)
            l1caches.append(c)

        client = ZipfClient(name=f"client_pop{pop}", cbase=1000, n=20000, p=0.3, a=1.1,
                            arrival=Poisson(lam=300, ticks=3600))
        for l1 in l1caches:
            client.connect_to(l1)
        pops.append([*l2caches, *l1caches, client])

    # run simulation
    try:
        ZipfClient.start_all()
        ZipfClient.join_all()
    except KeyboardInterrupt:
        pass
    finally:
        ZipfClient.terminate_all()
