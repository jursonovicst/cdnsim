from abc import ABC, abstractmethod
from multiprocessing import Process, Queue
from typing import List, Iterator, Any


class Node(Process, ABC):
    """
    General Node definition.
    """
    # keep track of nodes
    __nodes = []

    @classmethod
    def nodes(cls) -> List[Any]:
        return cls.__nodes

    @classmethod
    def start_all(cls) -> None:
        for node in cls.__nodes:
            node.start()

    @classmethod
    def terminate_all(cls) -> None:
        while Node.__nodes:
            node = Node.__nodes.pop()
            if node.is_alive():
                node.terminate()
                node.join(1)

    def __init__(self, name: str | None):
        """

        :param name: just for convenience, no function.
        """
        super().__init__(name=name)

        # register nodes
        Node.__nodes.append(self)

    def terminate(self) -> None:
        super().terminate()

        # deregister nodes
        if self in Node.__nodes:
            Node.__nodes.remove(self)

    @abstractmethod
    def run(self) -> None:
        """
        Implement this to do work with the nodes.
        """
        pass


class LNode(Node, ABC):
    """
    Defines nodes with message input(s). LNodes possess the message queue.
    """

    def __init__(self, name: str):
        super().__init__(name=name)
        self.__queue = Queue()

    def put(self, msg: Any, timeout: float = None) -> None:
        """
        Send messae to this nodes.
        :param msg:
        :param timeout:
        """
        self.__queue.put(msg, timeout=timeout)

    def _receive(self, timeout: float = None) -> Iterator[List[Any]]:
        """
        Iterator to process messages.
        :param timeout:
        :return:
        """
        while True:
            yield self.__queue.get(timeout=timeout)


class TNode(Node, ABC):
    """
    Defines nodes with message output(s).
    """

    def __init__(self, name: str):
        super().__init__(name=name)
        self.__remotes = []

    @property
    def remotes(self) -> List[LNode]:
        return self.__remotes

    def connect_to(self, remote: LNode) -> None:
        """
        Connect nodes to an other LNode. Connetion only works in message sending direction.
        :param remote: remote LNode.
        :return:
        """
        if not isinstance(remote, LNode):
            raise ValueError(f"Cannot connect to {remote.__class__.__name__}")
        if remote in self.__remotes:
            raise KeyError(f"Already connected to {remote.name}")
        self.__remotes.append(remote)


class XNode(LNode, TNode, ABC):
    """
    Defines nodes with message input(s) and output(s)
    """


class YNode(XNode, ABC):
    """
    Defines nodes with input(s) but only one output.
    """

    def connect_to(self, remote):
        if len(self.remotes) != 0:
            raise SyntaxError(f"{self.__class__.__name__} can connect only to one LNode!")
        super().connect_to(remote)
