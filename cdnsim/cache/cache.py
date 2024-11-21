from abc import ABC

from nodes.log import LoggerMixIn
from nodes.node import XNode


class Cache(LoggerMixIn, XNode, ABC):
    ...
