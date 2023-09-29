from abc import ABC, abstractmethod
from multiprocessing import Process
from multiprocessing import Queue as Queue
from typing import List, Iterator, Any

from cdnsim.log import LogMixIn


class Node(Process, LogMixIn, ABC):
    """
    General Node definition. Independent from any emulation, just provides a framework for general messaging amd
    multiprocessing.
    """
    # keep track of node
    __nodes = []

    @classmethod
    def start_all(cls) -> None:
        for node in cls.__nodes:
            print(f"Start {node.name}")
            node.start()

    @classmethod
    def terminate_all(cls) -> None:
        while Node.__nodes:
            node = Node.__nodes.pop()
            if node.is_alive():
                print(f"Terminate {node.name}")
                node.terminate()
                node.join(1)

    @classmethod
    def join_all(cls, timeout: float = None) -> None:
        for node in cls.__nodes:
            if node.is_alive():
                print(f"Join {node.name}")
                node.join(timeout)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._stats = {}
        Node.__nodes.append(self)

    def run(self) -> None:
        self._info(f"{self.name} started")
        try:
            self.work()
        except KeyboardInterrupt:
            pass
        finally:
            # deregister node
            if self in self.__nodes:
                self._info(f"{self.name} exited")
                self.__nodes.remove(self)

    @abstractmethod
    def work(self) -> None:
        ...


class LNode(Node, ABC):
    """
    Defines node with message input(s). LNodes possess the message queue.
    """

    def __init__(self, qsize=100, **kwargs):
        self.__queues = []
        self.__qsize = qsize
        self.__tick = 0
        super().__init__(**kwargs)

    @property
    def tick(self) -> int:
        return self.__tick

    def registerqueue(self) -> Queue:
        queue = Queue(self.__qsize)
        self.__queues.append(queue)
        return queue

    def _receive(self) -> Iterator[List[Any]]:
        """
        Iterator to process messages.
        :param timeout:
        :return:
        """
        while True:
            try:
                yield [msg for q in self.__queues for msg in q.get()]
                self.__tick += 1
            except KeyboardInterrupt:
                break


class TNode(Node, ABC):
    """
    Defines node with message output(s).
    """

    def __init__(self, **kwargs):
        self.__rqueues: dict[str, Queue] = {}
        super().__init__(**kwargs)

    @property
    def remotes(self) -> List[str]:
        return list(self.__rqueues.keys())

    def connect_to(self, remote: LNode) -> None:
        """
        Connect node to another LNode. Connetion only works in message sending direction.
        :param remote: remote LNode.
        :return:
        """
        if not isinstance(remote, LNode):
            raise ValueError(f"Cannot connect to {remote.__class__.__name__}")
        if remote.name in self.__rqueues.keys():
            raise KeyError(f"Already connected to {remote.name}")
        self.__rqueues[remote.name] = remote.registerqueue()

    def _send(self, to: str, msg: Any) -> None:
        try:
            self.__rqueues[to].put(msg)
        except KeyError as e:
            raise SyntaxError(f"Remote {e} not connected with us!")
        except KeyboardInterrupt:
            pass


class XNode(LNode, TNode, ABC):
    """
    Defines node with message input(s) and output(s)
    """


class YNode(XNode, ABC):
    """
    Defines node with input(s) but only one output.
    """

    def connect_to(self, remote: LNode) -> None:
        if len(self.__rqueues) != 0:
            raise SyntaxError(f"{self.__class__.__name__} can connect only to one LNode!")
        super().connect_to(remote)
