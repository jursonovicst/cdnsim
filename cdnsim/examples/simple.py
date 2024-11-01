from cdnsim import Client, Origin
from cdnsim.arrival import Poisson
from cdnsim.cache import NonCache
from cdnsim.requests import Zipf

if __name__ == "__main__":
    client1 = Client(arrival=Poisson(lam=100), requests=Zipf(cbase=10, a=1.1))
    client2 = Client(arrival=Poisson(lam=100), requests=Zipf(cbase=10, a=1.1))
    cache = NonCache()
    origin = Origin()

    client1.connect_to(cache)
    client2.connect_to(cache)
    cache.connect_to(origin)

    try:
        client1.start_all()
        client1.join_all()
    except KeyboardInterrupt:
        pass
    finally:
        client1.terminate()
