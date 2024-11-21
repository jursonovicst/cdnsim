from constant import Constant
from nodes.log import LogMixIn, LoggerMixIn
from noncache import NonCache
from origin import Origin
from uniform import Uniform

LoggerMixIn.setlevel(LogMixIn.INFO)

if __name__ == "__main__":

    # create the nodes
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

    # get stats
    ...
