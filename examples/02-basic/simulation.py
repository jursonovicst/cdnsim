from nodes.log import LogMixIn, LoggerMixIn

# Create the simplest CDN setup consisting of one client, one cache and a single origin.
#
# [client1] --> [cache1] --> [origin]
#
# the client requests uniform profiles according to a constant arrival processes, the caches are NonCaches, meaning,
# they do not cache at all (for demonstration purposes), and the origin just logs the number of requests received.

LoggerMixIn.setlevel(LogMixIn.INFO)

# the constant arrival process
from cdnsim.arrival import Arrival


class Constant(Arrival):
    """
    Constant arrival process. *rate* number of arrivals in every tick.
    """

    def __init__(self, rate: float, **kwargs):
        super().__init__(**kwargs)
        self.__rate = rate

    def __next__(self) -> int:
        super().__next__()
        return int(self.__rate)


# the uniform client implementation
from typing import Iterator, List, Tuple

import numpy as np
from scipy.stats import randint

from cdnsim import Client
from cdnsim.arrival import Arrival
from cdnsim.requests import BaseRequests


class Uniform(Client):
    """
    Uniform client, *cbase* number of contents, each content is requested with the same probability.
    """

    def __init__(self, cbase: int, arrival: Arrival, **kwargs):
        self._cbase = cbase
        self._arrival = arrival
        super().__init__(**kwargs)

    def _generate(self) -> Iterator[List[Tuple[str, BaseRequests]]]:
        for k in self._arrival:
            r = np.unique(randint.rvs(1, self._cbase + 1, size=k), return_counts=True)
            yield [(remote, request) for remote, request in
                   zip(self.remotes,
                       BaseRequests(freqs=list(r[1]), index={'content': list(r[0])}) // len(self.remotes))]


# noncache implementation

from cdnsim.cache import Cache


class NonCache(Cache):
    """
    For demonstration purposes, a non caching cache implementation.
    """

    def _work(self) -> None:
        # receive messages from all remotes until termination (empty list) received
        while msgs := self._receive():
            assert isinstance(msgs, list) and len(msgs) > 0, msgs

            # merge incoming requests
            requests = cast(BaseRequests, sum(msgs))

            # simply split the incoming requests among the remotes into equal parts
            for remote, split_requests in zip(self.remotes, requests // len(self.remotes)):
                self._send(remote, split_requests)


# origin implementation
from typing import cast

from cdnsim.requests import BaseRequests
from nodes.log import LoggerMixIn
from nodes.node import LNode


class Origin(LoggerMixIn, LNode):
    """
    Simple origin implementation. Logs the number of requests received.
    """

    def _work(self) -> None:
        # receive messages from all remotes until termination (empty list) received
        while msgs := self._receive():
            assert isinstance(msgs, list) and len(msgs) > 0, msgs

            # merge incoming requests
            requests = cast(BaseRequests, sum(msgs))

            # log number of requests received
            self._log(f"received {requests.sum()} requests")


if __name__ == "__main__":

    # create nodes
    client = Uniform(cbase=20, arrival=Constant(rate=50, ticks=5))
    cache = NonCache()
    origin = Origin()

    # establish connections
    client.connect_to(cache)
    cache.connect_to(origin)

    # run simulation
    try:
        client.start_all()
        client.join_all()
    except KeyboardInterrupt:
        pass
    finally:
        client.terminate()
