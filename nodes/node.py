from abc import ABC, abstractmethod, ABCMeta
from queue import Queue, ShutDown
from threading import Thread
from typing import List, Self

from nodes.log import LogMixIn


class Node(Thread, LogMixIn, metaclass=ABCMeta):
    """
    Abstract Base Class for Node definition, threading, and simulation control.
    """
    # keep track of nodes (threads)
    __nodes: List[Self] = []

    # default message queue size
    queuesize = 5

    @classmethod
    def start_all(cls) -> None:
        """
        Start the simulation.

        :return: None
        """
        for node in cls.__nodes: node.start()

    @classmethod
    def terminate_all(cls, timeout: float | None) -> None:
        """
        Terminate the simulation and wait for Node completion.

        :param timeout: timeout of individual nodes, une None for waiting indefinitely
        :return: None
        """
        while Node.__nodes:
            node = Node.__nodes.pop()
            if node.is_alive():
                node.terminate()
                node.join(timeout)
                if node.is_alive():
                    print(f"Termination of {node.name} failed within {timeout} seconds")  # TODO: add general logging

    @classmethod
    def join_all(cls) -> None:
        """
        Join the simulation, wait until completes. This call will block.

        :return: None
        """
        # join ignores KeyboardInterrupt, so this strange construct is needed to let the exception through
        while any([node.is_alive() for node in cls.__nodes]):
            for node in cls.__nodes:
                if node.is_alive():
                    node.join(0.1)

    @classmethod
    def list_all(cls) -> list[Self]:
        return cls.__nodes

    def __init__(self, name: str = '', **kwargs):
        kwargs.pop('target', None)
        super().__init__(name=name if name != '' else f"{self.__class__.__name__}-{id(self)}", target=self._work,
                         **kwargs)

        # register node
        Node.__nodes.append(self)

    @abstractmethod
    def terminate(self) -> None:
        ...

    def run(self) -> None:
        try:
            super().run()
        except ShutDown:
            pass
        self._log("Exit")

    @abstractmethod
    def _work(self, *args) -> None:
        """
        Overwrite this to implement your own node. You may use Process' *args* parameter in the constructor to provide custom
        variables.

        :return: None
        """
        ...


class LNode(Node, ABC):
    """
    Provides internode messaging by implementing a message input via multiprocessing.Queue.

    Letter L: assuming a top-down message flow, messages can enter via the vertical line of 'L', but output is blocked
    by the horizontal line.
    """

    def __init__(self, qsize=Node.queuesize, **kwargs):
        """
        :param qsize: number of on the fly messages
        """
        self.__queues = {}  # queues for message inputs
        self.__qsize = qsize
        super().__init__(**kwargs)

    def registerqueue(self, name: str) -> Queue:
        """
        Used by t-nodes connecting to this node. Creates the input queue.

        :param name: upstream node name
        """
        queue = Queue(self.__qsize)
        self.__queues[name] = queue
        return queue

    def terminate(self) -> None:
        for queue in self.__queues.values(): queue.shutdown()

    @property
    def upstreams(self) -> List[str]:
        """
        Returns the name of the upstream connected nodes.
        """
        return list(self.__queues.keys())

    def _receive(self) -> list:
        """
        Receives messages from all inputs. It will wait till one message is received from all input queues.

        :return: the next messages from the message queues
        """
        # collect messages from all upstreams
        return [queue.get() for queue in self.__queues.values()]


class TNode(Node, ABC):
    """
    Provides internode messaging by implementing a message output.

    Letter T: assuming a top-down message flow, messages can exit via the vertical line of 'T', but input is blocked by
    the horizontal line.
    """

    def __init__(self, **kwargs):
        self.__rqueues: dict[str, Queue] = {}
        super().__init__(**kwargs)

    def connect_to(self, remote: LNode) -> None:
        """
        Connect this TNode to another LNode. Connection only works from sender to receiver direction.

        :param remote: remote LNode.
        :return: None
        """
        if not isinstance(remote, LNode):
            raise ValueError(f"Cannot connect to {remote.__class__.__name__}, not an LNode!")
        if remote.name in self.__rqueues.keys():
            raise KeyError(f"Already connected to {remote.name}")
        self.__rqueues[remote.name] = remote.registerqueue(self.name)

    def terminate(self) -> None:
        for rqueue in self.__rqueues.values(): rqueue.shutdown()

    def run(self) -> None:
        super().run()

        # completed or terminated, shut down the remote queue to unblock put() and get() methods.
        for rqueue in self.__rqueues.values():
            rqueue.shutdown()

    @property
    def downstreams(self) -> List[str]:
        """
        Returns the name of the downstream connected nodes.
        """
        return list(self.__rqueues.keys())

    def _send(self, msgs: list) -> None:
        if len(msgs) != len(self.__rqueues):
            raise ValueError(f"Message number mismatch: {len(msgs)} messages but {len(self.__rqueues)} downstreams.")

        for queue, msg in zip(self.__rqueues.values(), msgs):
            queue.put(msg)


class INode(LNode, TNode, ABC):
    """
    Provides internode messaging by implementing inputs and outputs.
    """
