from abc import ABC

from nodes.log import LoggerMixIn
from nodes.node import TNode


class Client(LoggerMixIn, TNode, ABC):
    ...
