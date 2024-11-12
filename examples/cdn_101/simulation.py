from cdnsim import Client, Origin
from plfucache import PLFUCache
from poisson import Poisson
from zipf import Zipf

# Create a simple CDN setup consisting of two clients, two caches and a single origin.
#
# [client1] -┐┌-> [cache1] -┐
#            ├┤             ├-> [cache3] --> [origin]
# [client2] -┘└-> [cache2] -┘
#
# the clients are requesting different profiles of Zipf distribution according to different arrival processes, the
# caches are NonCaches, meaning, they do not cache at all (just for this example), and the origin is a simple origin.


if __name__ == "__main__":
    # create the nodes
    client1 = Client(arrival=Poisson(lam=50), requests=Zipf(cbase=20, a=1.6))
    client2 = Client(arrival=Poisson(lam=80), requests=Zipf(cbase=100, a=1.1))
    cache1 = PLFUCache(size=10)
    cache2 = PLFUCache(size=10)
    cache3 = PLFUCache(size=20)
    origin = Origin()

    # second, establish connections
    client1.connect_to(cache1)
    client1.connect_to(cache2)
    client2.connect_to(cache1)
    client2.connect_to(cache2)
    cache1.connect_to(cache3)
    cache2.connect_to(cache3)
    cache3.connect_to(origin)

    # third, run simulation
    try:
        client1.start_all()
        client1.join_all()
    except KeyboardInterrupt:
        pass
    finally:
        client1.terminate()

    # fourth, get stats
