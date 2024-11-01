from .log import LogMixIn


class LoggerMixIn(LogMixIn):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _info(self, buff: str) -> None:
        print(buff)
