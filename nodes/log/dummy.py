import logging

from nodes.log import LogMixIn, LogLevel


class DummylogMixIn(LogMixIn):
    @classmethod
    def setlevel(cls, loglevel: LogLevel) -> None:
        pass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _log(self, buff: str, severity: str = LogMixIn.INFO) -> None:
        pass

    def _exception(self, buff: str) -> None:
        logging.exception(buff)
