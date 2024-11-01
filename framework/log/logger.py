from abc import ABC

from framework.node import Node
from .log import LogMixIn


class LoggerMixIn(Node, LogMixIn, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def log(self, buff: str, severity: str = LogMixIn.INFO) -> None:
        print(f"{self.name} {severity}: {buff}")
