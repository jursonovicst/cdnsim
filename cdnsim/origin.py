from abc import ABC

from nodes.log import LoggerMixIn
from nodes.node import LNode


class Origin(LoggerMixIn, LNode, ABC):
    ...
