from cdnsim import Client, Origin
from constant import Constant
from noncache import NonCache
from uniform import Uniform


if __name__ == "__main__":
    # create the nodes
    client = Client(arrival=Constant(rate=50), requests=Uniform(cbase=20))
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

    # get stats
    ...
