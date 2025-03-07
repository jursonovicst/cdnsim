from abc import ABC

from nodes.log import LoggerMixIn
from nodes.node import INode


class Cache(LoggerMixIn, INode, ABC):
    ...
