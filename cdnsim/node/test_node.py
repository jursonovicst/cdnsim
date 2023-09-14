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

        # initially, no registered nodes
        self.assertListEqual([], SendNode.nodes())

        # regsiter 2 nodes, should be unconnected
        sender = SendNode('sender')
        receiver = RecvNode('receiver')
        self.assertListEqual(['sender', 'receiver'], SendNode.nodes())
        self.assertEqual(0, len(sender.remote_lnodes), sender.remote_lnodes)
        self.assertEqual(0, len(receiver.remote_tnodes), receiver.remote_tnodes)

        # connect nodes
        sender.connect_to(receiver)
        self.assertListEqual(['receiver'], sender.remote_lnodes)
        self.assertListEqual(['sender'], receiver.remote_tnodes)

        # connect invalid
        with self.assertRaises(ValueError):
            sender.connect_to(sender)

        # send message
        sender._sendto('tom', receiver)
        self.assertListEqual(['tom'], next(receiver._receive()))

        # send to non-connected node
        with self.assertRaises(KeyError):
            sender._sendto('tom', sender)

        # reverse connect multiple
        sender2 = SendNode('sender2')
        receiver.connect_to(sender2)
        self.assertListEqual(['receiver'], sender.remote_lnodes)
        self.assertListEqual(['receiver'], sender2.remote_lnodes)
        self.assertListEqual(['sender', 'sender2'], receiver.remote_tnodes)

        # send multiple
        sender._sendto('tom1', receiver)
        sender2._sendto('tom2', receiver)
        self.assertListEqual(['tom1', 'tom2'], next(receiver._receive()))

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
        receiver.connect_to(middle)
        self.assertListEqual(['middle'], sender.remote_lnodes)
        self.assertListEqual(['receiver'], middle.remote_lnodes)
        self.assertListEqual(['sender'], middle.remote_tnodes)
        self.assertListEqual(['middle'], receiver.remote_tnodes)

        # send
        sender._sendto('tom', middle)
        self.assertListEqual(['tom'], next(middle._receive()))

        middle._sendto('tom', receiver)
        self.assertListEqual(['tom'], next(receiver._receive()))
