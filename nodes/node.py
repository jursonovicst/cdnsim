from abc import ABC, abstractmethod, ABCMeta
from multiprocessing import Process
from multiprocessing import Queue as Queue
from typing import List, Any, Self

from nodes.log import LogMixIn


class Node(Process, LogMixIn, metaclass=ABCMeta):
    """
    General Node definition for multiprocessing and simulation start/stop features.
    """
    # keep track of nodes
    __nodes: List[Self] = []

    @classmethod
    def start_all(cls) -> None:
        """
        Start the simulation

        :return: None
        """
        for node in cls.__nodes:
            node._log(f"Start {node.name}", LogMixIn.INFO)
            node.start()

    @classmethod
    def terminate_all(cls, timeout: float = None) -> None:
        """
        Terminate the simulation and wait for Node completion.

        :param timeout: timeout of individual nodes, defaults to None (wait indefinitely)
        :return: None
        """
        while Node.__nodes:
            node = Node.__nodes.pop()
            if node.is_alive():
                node._log(f"Terminate {node.name}", LogMixIn.INFO)
                node.terminate()
                node.join(timeout)

    @classmethod
    def join_all(cls) -> None:
        """
        Join the simulation, wait until completes. This call will block.

        :return: None
        """
        for node in cls.__nodes:
            if node.is_alive():
                node._log(f"Join {node.name}", LogMixIn.INFO)
                node.join()

    @classmethod
    def list_all(cls) -> List[Self]:
        return cls.__nodes

    def __init__(self, **kwargs):
        # Make class's run method provate. Developers should use the work method to implement custom tasks.
        kwargs['target'] = self._run

        super().__init__(**kwargs)
        self._stats = {}

        # register node
        Node.__nodes.append(self)

    def _run(self) -> None:
        """
        Private method, use the work method to implement custom tasks.

        :return: None
        """
        self._log(f"{self.name} started")
        try:
            self._work()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            self._exception(f"unexpected exception while running node: {e}")
        finally:
            self._log(f"{self.name} exited")

            # deregister exited node
            #  self.__nodes.remove(self) # TODO: this is not working (node not on list exception). Figure out why...

    @abstractmethod
    def _work(self) -> None:
        """
        Overwrite this to implement your custom node.

        :return: None
        """
        ...


class LNode(Node, ABC):
    """
    Provides inter-node messaging by implementing a message input via multiprocessing.Queue.

    Letter L: assuming a top-down message flow, messages can enter via the vertical line of 'L', but output is blocked
    by the horizontal line.
    """

    def __init__(self, qsize=100, **kwargs):
        """
        :param qsize: number of on the fly messages
        """
        self.__queues = []  # queues for message inputs
        self.__qsize = qsize
        self._nreceived = 0  # counter of processed messages
        super().__init__(**kwargs)

    #    @property
    #    def tick(self) -> int:
    #        return self._nreceived

    def registerqueue(self) -> Queue:
        queue = Queue(self.__qsize)
        self.__queues.append(queue)
        return queue

    def _receive(self) -> List[Any]:
        """
        Iterator to process messages. It will wait till one message is received in all input queues.

        :return: the next messages from the message queues
        """
        msgs = [q.get() for q in self.__queues]
        self._nreceived += 1  # update received no.
        return msgs


class TNode(Node, ABC):
    """
    Provides inter-node messaging by implementing a message output.

    Letter T: assuming a top-down message flow, messages can exit via the vertical line of 'T', but input is blocked by
    the horizontal line.
    """

    def __init__(self, **kwargs):
        self.__rqueues: dict[str, Queue] = {}
        super().__init__(**kwargs)

    @property
    def remotes(self) -> List[str]:
        """
        Remote (connected) nodes

        :return: list of remote node names
        """
        return list(self.__rqueues.keys())

    def connect_to(self, remote: LNode) -> None:
        """
        Connect this TNode to another LNode. Connection only works from sender to receiver direction.

        :param remote: remote LNode.
        :return: None
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
    Provides inter-node messaging by implementing inputs and outputs.
    """


class YNode(TNode, LNode, ABC):
    """
    Provides inter-node messaging by implementing inputs and a single output.
    """

    def connect_to(self, remote: LNode) -> None:
        if len(self.remotes) != 0:
            raise SyntaxError(f"{self.__class__.__name__} can connect only to one LNode!")
        super().connect_to(remote)

    @property
    def remote(self) -> LNode | None:
        return None if not self.remotes else self.remotes[0]
