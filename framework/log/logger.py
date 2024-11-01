from framework.log import LogMixIn


class LoggerMixIn(LogMixIn):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def log(self, buff: str, severity: str = LogMixIn.INFO) -> None:
        print(f"{self.name} {severity}: {buff}")
