from cdnsim.content import Obj
from cdnsim.log import LogMixIn


class LoggerMixIn(LogMixIn):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _info(self, buff: str) -> None:
        print(buff)

    def _request(self, tick: int, obj: Obj) -> None:
        print(f"{tick}: {str(obj)}")
