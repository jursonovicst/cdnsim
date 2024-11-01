import time

from framework.log import LoggerMixIn
from framework.node import LNode, TNode, XNode


class Client(LoggerMixIn, TNode):
    """
    generates a sequence of numbers
    """

    def work(self) -> None:
        i = 0
        while True:
            time.sleep(1)
            for remote in self.remotes:
                self._send(remote, i)
                i += 1


class Repeater(LoggerMixIn, XNode):
    """
    replicates all incoming messages to all receivers
    """

    def work(self) -> None:
        while True:
            for msg in self._receive():
                for remote in self.remotes:
                    self._send(remote, msg)


class Origin(LoggerMixIn, LNode):
    """
    logs received messages
    """

    def work(self) -> None:
        while True:
            for msg in self._receive():
                self.log(msg)


if __name__ == "__main__":
    try:
        client = Client(name="client")
        repeater = Repeater(name="repeater")
        origin1 = Origin(name="origin1")
        origin2 = Origin(name="origin2")
        client.connect_to(repeater)
        repeater.connect_to(origin1)
        repeater.connect_to(origin2)
        client.start_all()
        client.join_all()
    except KeyboardInterrupt:
        pass
    finally:
        Client.terminate_all()
