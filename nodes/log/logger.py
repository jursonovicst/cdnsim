import logging
from logging import getLogger

from nodes.log import LogMixIn, LogLevel


# TODO: figure _out, how to add inheritance here from Node (to access the .node property), without circular reference.
class LoggerMixIn(LogMixIn):
    __sev2level = {LogLevel.INFO: logging.INFO, LogLevel.DEBUG: logging.DEBUG}

    @classmethod
    def setlevel(cls, loglevel: LogLevel) -> None:
        logging.basicConfig(level=cls.__sev2level[loglevel])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__logger = getLogger(self.name)

    def _log(self, buff: str, severity: LogLevel = LogMixIn.INFO) -> None:
        self.__logger.log(self.__sev2level[severity], buff)

    def _exception(self, buff: str = "Unexpected exception") -> None:
        self.__logger.exception(buff)
