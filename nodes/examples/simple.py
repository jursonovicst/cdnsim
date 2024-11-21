import time

from nodes.log import LoggerMixIn, LogLevel
from nodes.node import LNode, TNode, XNode

# With the help of the nodes framework, we will implement a very basic example of nodes and their communication:
#
#                          ┌-> [receiver1]
# [sender] --> [repeater] -┤
#                          └-> [receiver2]
#
# sender:   sends a sequence of numbers in every second
# repeater: just forwards all messages from its inputs to its outputs
# receiver: just receives (and prints) all messages
#
# we expect, that the simulation will log the numbers from 0 on, two times each (by receiver 1 and receiver2).

LoggerMixIn.setlevel(LogLevel.INFO)


# first, create the Sender class to implement the sender function, for that, we will need a **TNode** for message
# outputs and a LogMixIn to provide logger functions for the TNode
class Sender(LoggerMixIn, TNode):
    """
    Sends a sequence of numbers in every second
    """

    def _work(self) -> None:
        i = 0
        while True:
            time.sleep(1)
            for remote in self.remotes:
                self._send(remote, i)
                i += 1


# second, implement the repeater function by using an XNode
class Repeater(LoggerMixIn, XNode):
    """
    Replicates all incoming messages to all receivers
    """

    def _work(self) -> None:
        while True:
            for msg in self._receive():
                for remote in self.remotes:
                    self._send(remote, msg)


# third, implement the receiver by using an LNode
class Receover(LoggerMixIn, LNode):
    """
    Logs received messages
    """

    def _work(self) -> None:
        while True:
            for msg in self._receive():
                self._log(msg)


if __name__ == "__main__":
    try:
        # fourth, instantiate the required functions
        sender = Sender(name="client")
        repeater = Repeater(name="repeater")
        receiver1 = Receover(name="origin1")
        receiver2 = Receover(name="origin2")

        # fifth, connect the nodes according to the communication plan
        sender.connect_to(repeater)
        repeater.connect_to(receiver1)
        repeater.connect_to(receiver2)

        # sixth, start the simulation, and wait for the results.
        sender.start_all()
        sender.join_all()
    except KeyboardInterrupt:
        pass
    finally:
        Sender.terminate_all()