from unittest import TestCase

from cdnsim.node import Node, LNode, TNode, XNode


class TestNode(TestCase):
    def setUp(self) -> None:
        Node.terminate_all()

    def tearDown(self) -> None:
        Node.terminate_all()

    def test_LTNode(self):
        class RecvNode(LNode):
            def run(self) -> None:
                pass

        class SendNode(TNode):
            def run(self) -> None:
                pass

        # initially, no registered node
        self.assertListEqual([], SendNode.nodes())

        # regsiter 2 node, should be unconnected
        sender = SendNode('sender')
        receiver = RecvNode('receiver')
        self.assertListEqual([sender, receiver], SendNode.nodes())
        self.assertEqual(0, len(sender.remotes))

        # connect node
        sender.connect_to(receiver)
        self.assertListEqual([receiver], sender.remotes)

        # connect invalid
        with self.assertRaises(ValueError):
            sender.connect_to(sender)

        # send message
        sender.remotes[0].put('tom')
        self.assertEqual('tom', next(receiver._receive()))

        # send multiple
        sender2 = SendNode('sender2')
        sender2.connect_to(receiver)
        sender.remotes[0].put('tom1')
        sender2.remotes[0].put('tom2')
        self.assertListEqual(['tom1', 'tom2'], [next(receiver._receive()), next(receiver._receive())])

    def test_XNode(self):
        class SendNode(TNode):
            def run(self) -> None:
                pass

        class MiddleNode(XNode):
            def run(self) -> None:
                pass

        class RecvNode(LNode):
            def run(self) -> None:
                pass

        sender = SendNode('sender')
        middle = MiddleNode("middle")
        receiver = RecvNode('receiver')

        # connect and reverse connect
        sender.connect_to(middle)
        middle.connect_to(receiver)
        self.assertListEqual([middle], sender.remotes)
        self.assertListEqual([receiver], middle.remotes)

        # send
        sender.remotes[0].put('tom')
        self.assertEqual('tom', next(middle._receive()))

        middle.remotes[0].put('tom')
        self.assertEqual('tom', next(receiver._receive()))
