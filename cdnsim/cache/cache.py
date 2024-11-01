from abc import ABC

from framework.log import LoggerMixIn
from framework.node import XNode


class Cache(XNode, LoggerMixIn, ABC):
    ...
