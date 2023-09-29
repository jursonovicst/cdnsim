from cdnsim.arrival import PoissonMixIn
from cdnsim.content import ZipfMixIn, Obj
from cdnsim.log import LoggerMixIn
from cdnsim.node import LNode, TNode, XNode


class Client(PoissonMixIn, ZipfMixIn, LoggerMixIn, TNode):

    def work(self) -> None:
        for size in self._arrival():
            self._send(self.remotes[0], self._content(size))


class Origin(LoggerMixIn, LNode):

    def work(self) -> None:
        for msg in self._receive():
            for obj in msg:
                self._request(self.tick, obj)


class Cache(LoggerMixIn, XNode):
    def work(self) -> None:
        for msg in self._receive():
            self._send(self.remotes[0], msg)


if __name__ == "__main__":
    try:
        client = Client(name="client1", lam=1, alpha=1.2, content_base=[Obj(i) for i in range(1000)])
        cache = Cache(name='cache1')
        origin = Origin(name="origin1")
        client.connect_to(cache)
        cache.connect_to(origin)

        client.start_all()
        client.join_all()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
    finally:
        Client.terminate_all()
