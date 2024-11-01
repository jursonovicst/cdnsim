from abc import ABC

from cdnsim.requests import RequestMixIn
from framework.log import LoggerMixIn
from framework.node import XNode


class Cache(LoggerMixIn, RequestMixIn, XNode, ABC):
    ...
