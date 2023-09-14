from abc import ABC, abstractmethod
from multiprocessing import Process, Queue
from typing import List, Iterator, Any


class Node(Process, ABC):
    """
    General Node definition.
    """
    # keep track of nodes
    __nodes = {}

    @classmethod
    def nodes(cls) -> List[str]:
        return list(cls.__nodes.keys())

    @classmethod
    def start_all(cls) -> None:
        for node in cls.__nodes.values():
            node.start()

    @classmethod
    def terminate_all(cls) -> None:
        while Node.__nodes:
            name, node = Node.__nodes.popitem()
            if node.is_alive():
                node.terminate()
                node.join(1)

    def __init__(self, name: str):
        if name in Node.__nodes:
            raise KeyError(f"Node with name {name} already exists!")

        super().__init__(name=name)

        # register node
        Node.__nodes[name] = self

    def terminate(self) -> None:
        super().terminate()

        # deregister node
        if self.name in Node.__nodes:
            Node.__nodes.pop(self.name)

    @abstractmethod
    def run(self) -> None:
        """
        Implement this to do work with the node.
        """
        pass


class TNode(Node, ABC):
    """
    Defines node with message output(s).
    """

    def __init__(self, name: str):
        super().__init__(name=name)
        self.__remote_queues = {}

    @property
    def remote_lnodes(self) -> List[str]:
        return list(self.__remote_queues.keys())

    def connect_to(self, remote: Node):
        if not isinstance(remote, LNode):
            raise ValueError(f"Cannot connect to {remote.__class__.__name__}")
        if remote.name in self.__remote_queues:
            raise KeyError(f"Already connected to {remote.name}")
        self.__remote_queues[remote.name] = remote.create_queue_for(self)

    def register_queue_for(self, queue: Queue, lnode: Node):
        assert isinstance(lnode, LNode), f"Are you sure? {type(lnode)}"
        assert lnode.name not in self.__remote_queues, f"Queue already exist for {lnode.name}"
        self.__remote_queues[lnode.name] = queue

    def _sendto(self, msg: Any, node: Node, timeout: float = None) -> None:
        if node.name not in self.__remote_queues:
            raise KeyError(f"Not connected to node {node.name}")
        self.__remote_queues[node.name].put(msg, timeout=timeout)


class LNode(Node, ABC):
    """
    Defines node with message input(s).
    """

    def __init__(self, name: str):
        super().__init__(name=name)
        self.__queues = {}

    @property
    def remote_tnodes(self) -> List[str]:
        return list(self.__queues.keys())

    def connect_to(self, remote: Node):
        if not isinstance(remote, TNode):
            raise ValueError(f"{self.__class__.__name__} cannot connect to {remote.__class__.__name__}")
        if remote.name in self.__queues:
            raise KeyError(f"Already connected to {remote.name}")

        remote.register_queue_for(self.create_queue_for(remote), self)

    def create_queue_for(self, tnode: TNode) -> Queue:
        assert isinstance(tnode, TNode), f"Are you sure? {type(tnode)}"
        assert tnode.name not in self.__queues, f"Queue already exist for {tnode.name}"

        self.__queues[tnode.name] = Queue()
        return self.__queues[tnode.name]

    def _receive(self, timeout: float = None) -> Iterator[List[Any]]:
        while True:
            yield [q.get(timeout=timeout) for q in self.__queues.values()]


class XNode(LNode, TNode, ABC):
    """
    Defines node with message input(s) and output(s)
    """

    def connect_to(self, remote: Node):
        """
        Call connect only once.
        :param remote:
        :return:
        """
        if isinstance(remote, LNode):
            TNode.connect_to(self, remote)

        elif isinstance(remote, TNode):
            LNode.connect_to(self, remote)


class YNode(XNode, ABC):
    """
    Defines node with input(s) but only one output.
    """

    def connect_to(self, remote):
        assert len(self.remote_lnodes) == 0, f"{self.__class__.__name__} can connect only to one LNode!"
        super().connect_to(remote)


class ANode(XNode, ABC):
    """
    Defines node with only one input and output(s)
    """

    def connect_to(self, remote):
        assert len(self.remote_tnodes) == 0, f"{self.__class__.__name__} can connect only to one TNode!"
        super().connect_to(remote)
