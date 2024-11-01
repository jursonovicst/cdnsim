from framework.log import LogMixIn


class DummylogMixIn(LogMixIn):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def log(self, buff: str, severity: str = LogMixIn.INFO) -> None:
        pass
