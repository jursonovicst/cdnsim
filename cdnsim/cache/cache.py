from abc import ABC

from cdnsim.requests import IngressMixIn
from nodes.log import LoggerMixIn
from nodes.node import XNode


class Cache(LoggerMixIn, IngressMixIn, XNode, ABC):
    ...
