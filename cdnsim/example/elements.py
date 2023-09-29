from cdnsim.arrival import PoissonMixIn
from cdnsim.content import ZipfMixIn
from cdnsim.log import LoggerMixIn, InfluxMixIn
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


class Cache(XNode):
    def work(self) -> None:
        for msg in self._receive():
            self._send(self.remotes[0], msg)
