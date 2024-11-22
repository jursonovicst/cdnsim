from abc import ABC, abstractmethod, ABCMeta
from multiprocessing import Process
from multiprocessing import Queue as Queue
from typing import List, Any, Self

from nodes.log import LogMixIn, LogLevel


class Node(Process, LogMixIn, metaclass=ABCMeta):
    """
    Abstract Base Class for Node definition, multiprocessing and simulation start/stop features.
    """
    # keep track of nodes (=processes)
    __nodes: List[Self] = []

    @classmethod
    def start_all(cls) -> None:
        """
        Start the simulation

        :return: None
        """
        for node in cls.__nodes:
            node._log(f"Start {node.name}", LogMixIn.DEBUG)
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
                node._log(f"Terminate {node.name}", LogMixIn.DEBUG)
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
                node._log(f"Join {node.name}", LogMixIn.DEBUG)
                node.join()

    @classmethod
    def list_all(cls) -> List[Self]:
        return cls.__nodes

    def __init__(self, **kwargs):
        # Make class' run method private. Developers should use the _work method to implement custom tasks.
        kwargs.pop('target', None)

        super().__init__(target=self._run, **kwargs)
        self._stats = {}

        # register node
        Node.__nodes.append(self)

    def _run(self, *args) -> None:
        """
        Private method, use the work method to implement custom tasks.

        :return: None
        """
        self._log(f"started", LogLevel.INFO)
        try:
            self._work(*args)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            self._exception(f"unexpected exception while running node: {e}")
        finally:
            self._log(f"exited", LogLevel.INFO)

        # deregister exited node
        #  self.__nodes.remove(self) # TODO: this is not working (node not on list exception). Figure out why...

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

    def __init__(self, qsize=100, **kwargs):
        """
        :param qsize: number of on the fly messages
        """
        self.__queues = []  # queues for message inputs
        self.__qsize = qsize
        super().__init__(**kwargs)

    def registerqueue(self) -> Queue:
        """
        Used by T-nodes connecting to this node. Creates the input queue.
        """
        queue = Queue(self.__qsize)
        self.__queues.append(queue)
        return queue

    def _receive(self) -> List[Any]:
        """
        Receives messages from all inputs. It will wait till one message is received from all input queues.

        :return: the next messages from the message queues
        """
        # collect messages
        msgs = []
        for queue in self.__queues:
            # get message from the ith queue, remove queue if termination (None) message received
            if (msg := queue.get()) is None:
                queue.close()
                self.__queues.remove(queue)
            else:
                msgs.append(msg)

        return msgs


class TNode(Node, ABC):
    """
    Provides internode messaging by implementing a message output.

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

    def _run(self, *args) -> None:
        super()._run(*args)

        # _work() exited, send the termination message down the chain
        for rqueue in self.__rqueues.values():
            rqueue.put(None)

    def _send(self, to: str, msg: Any) -> None:
        if msg is None:
            raise ValueError("Cannot send None message, None is reserved for termination.")
        try:
            self.__rqueues[to].put(msg)
        except KeyError as e:
            raise SyntaxError(f"Remote {e} not connected with us!")
        except KeyboardInterrupt:
            pass


class XNode(LNode, TNode, ABC):
    """
    Provides internode messaging by implementing inputs and outputs.
    """


class YNode(TNode, LNode, ABC):
    """
    Provides internode messaging by implementing inputs and a single output.
    """

    def connect_to(self, remote: LNode) -> None:
        if len(self.remotes) != 0:
            raise SyntaxError(f"{self.__class__.__name__} can connect only to one LNode!")
        super().connect_to(remote)

    @property
    def remote(self) -> LNode | None:
        return None if not self.remotes else self.remotes[0]
