from urllib3 import request

from framework.log import LoggerMixIn
from framework.node import LNode


class Origin(LNode, LoggerMixIn):
    def work(self) -> None:
        while True:
            # merge requests
            #print(self._receive())
            requests = sum(self._receive())
            print(requests)



