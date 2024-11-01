from cdnsim import Client, Origin
from cdnsim.arrival import Poisson
from cdnsim.requests import Zipf
from cdnsim.cache import PLFUCache

if __name__ == "__main__":

    client1 = Client(arrival=Poisson(lam=100), requests=Zipf(cbase=10, a=1.1))
    client2 = Client(arrival=Poisson(lam=100), requests=Zipf(cbase=10, a=1.1))
#    cache = LFUCache()
    origin = Origin()

    client1.connect_to(origin)
    client2.connect_to(origin)
#    cache.connect_to(origin)

    client1.start_all()

