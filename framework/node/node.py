import logging
from abc import ABC, abstractmethod, ABCMeta
from multiprocessing import Process
from multiprocessing import Queue as Queue
from typing import List, Any

from framework.log import LogMixIn


class Node(Process, LogMixIn, metaclass=ABCMeta):
    """
    General Node definition. Provides a framework for general messaging amd multiprocessing.
    """
    # keep track of nodes
    __nodes = []

    @classmethod
    def start_all(cls) -> None:
        """
        Start the simulation
        """
        for node in cls.__nodes:
            logging.info(f"Start {node.name}")
            node.start()

    @classmethod
    def terminate_all(cls) -> None:
        """
        Terminate the simulation
        """
        while Node.__nodes:
            node = Node.__nodes.pop()
            if node.is_alive():
                logging.info(f"Terminate {node.name}")
                node.terminate()
                node.join(1)

    @classmethod
    def join_all(cls, timeout: float = None) -> None:
        """
        Join the simulation, wait until completes. This call blocks.
        """
        for node in cls.__nodes:
            if node.is_alive():
                logging.info(f"Join {node.name}")
                node.join(timeout)

    @classmethod
    def list_all(cls) -> list:
        return cls.__nodes

    def __init__(self, **kwargs):
        kwargs['target'] = self._run
        super().__init__(**kwargs)
        self._stats = {}
        Node.__nodes.append(self)

    def _run(self) -> None:
        """
        Use the work method to implement your own tasks.
        """
        self.log(f"{self.name} started")
        try:
            self.work()
        except KeyboardInterrupt:
            pass
        finally:
            self.log(f"{self.name} exited")

    @abstractmethod
    def work(self) -> None:
        """
        Overwrite this to implement your node.
        """
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

    def _receive(self) -> List[Any]:
        """
        Iterator to process messages.
        :param timeout:
        :return:
        """
        self.__tick += 1
        return [q.get() for q in self.__queues]


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
        Connect node to another LNode. Connection only works in message sending direction.
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


class YNode(TNode, LNode, ABC):
    """
    Defines node with input(s) but only one output.
    """

    def connect_to(self, remote: LNode) -> None:
        if len(self.remotes) != 0:
            raise SyntaxError(f"{self.__class__.__name__} can connect only to one LNode!")
        super().connect_to(remote)

    @property
    def remote(self) -> LNode | None:
        return None if not self.remotes else self.remotes[0]
