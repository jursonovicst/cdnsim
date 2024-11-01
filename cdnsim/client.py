from cdnsim.arrival import Arrival
from cdnsim.requests import Requests
from framework.log import LoggerMixIn
from framework.node import TNode


class Client(LoggerMixIn, TNode):
    def __init__(self, arrival: Arrival, requests: Requests, **kwargs):
        super().__init__(**kwargs)
        self._arrival = arrival
        self._requests = requests

    def work(self) -> None:
        for k in self._arrival:  # <-- number of client requests
            for remote in self.remotes:  # <-- upstream nodes
                self._send(remote, self._requests.generate(k) / len(self.remotes))  # <-- evenly distributed among nodes
