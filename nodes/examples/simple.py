import time

from nodes.log import LoggerMixIn
from nodes.node import LNode, TNode, INode

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
# we expect, that the simulation will log the numbers from 10 to 0, two times each (by receiver 1 and receiver2).

LoggerMixIn.setlevel(LoggerMixIn.DEBUG)


# Create the Sender class to implement the sender function, for that, we will need a **TNode** for messageoutputs and a
# LogMixIn to provide logger functions for the TNode
class Sender(LoggerMixIn, TNode):
    """
    Sends a sequence of numbers
    """

    def _work(self) -> None:
        i = 0
        while i < 10000:
            self._send([str(i)] * len(self.downstreams))
            i += 1


# Implement the repeater function by using an XNode
class Repeater(LoggerMixIn, INode):
    """
    Copies all incoming messages to all receivers
    """

    def _work(self) -> None:
        while msgs := self._receive():
            self._send([','.join(msgs)] * len(self.downstreams))


# Implement the receiver by using an LNode
class Receiver(LoggerMixIn, LNode):
    """
    Logs received messages
    """

    def _work(self) -> None:
        while msgs := self._receive():
            self._log(f"received {'.'.join(map(str, msgs))}", LoggerMixIn.INFO)


if __name__ == "__main__":
    try:
        # Instantiate the required functions
        sender = Sender(name="client")
        repeater = Repeater(name="repeater")
        receiver1 = Receiver(name="receiver1")
        receiver2 = Receiver(name="receiver2")

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
        Sender.terminate_all(2)

    time.sleep(1)
