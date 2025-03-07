from pathlib import Path
from unittest import TestCase

from nodes.log import DummylogMixIn
from nodes.node import Node, LNode, TNode, INode


class MyNode(Node, DummylogMixIn):
    def _work(self) -> None:
        Path('_out/test.txt').touch()

    def terminate(self) -> None:
        pass


class MyTNode(TNode, DummylogMixIn):
    """
    Sends one *msg* message, then terminates.
    """

    def __init__(self, msg: str, **kwargs):
        super().__init__(**kwargs, args=(msg,))

    def _work(self, msg) -> None:
        self._send([msg] * len(self.downstreams))


class MyLNode(LNode, DummylogMixIn):
    """
    Receives messages.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._msg = ''

    def _work(self) -> None:
        self._msg = ','.join(self._receive())

    def getmsgs(self) -> str:
        return self._msg


class TestNode(TestCase):
    def setUp(self) -> None:
        Node.terminate_all(1)

    def tearDown(self) -> None:
        Node.terminate_all(1)

    def test_node(self):
        # simplest node implementation
        node1 = MyNode(name='Tom')
        self.assertEqual('Tom', node1.name, node1.name)
        self.assertEqual(1, len(Node.list_all()))
        self.assertEqual('Tom', Node.list_all()[0].name)

        # check work function
        Path('_out/test.txt').unlink(missing_ok=True)
        MyNode.start_all()
        MyNode.join_all()
        self.assertEqual(1, len(Node.list_all()), "tpm")
        self.assertTrue(Path('_out/test.txt').exists())

        MyNode.terminate_all(1)
        self.assertEqual(0, len(Node.list_all()), "tpm")

        node2 = MyNode(name="tom")
        self.assertEqual("tom", node2.name)

    def test_LTNode(self):
        # initially, no registered node
        # self.assertListEqual([], Node.__nodes)

        # regsiter 2 node, should be unconnected
        sender1 = MyTNode(name='sender1', msg='hello1')
        sender2 = MyTNode(name='sender2', msg='hello2')
        receiver = MyLNode(name='receiver')
        self.assertEqual(0, len(sender1.downstreams))

        # connect node
        sender1.connect_to(receiver)
        sender2.connect_to(receiver)
        self.assertListEqual([receiver.name], sender1.downstreams)
        self.assertListEqual([receiver.name], sender2.downstreams)
        self.assertListEqual([sender1.name, sender2.name], receiver.upstreams)

        # connect invalid
        with self.assertRaises(ValueError):
            sender1.connect_to(sender2)

        MyTNode.start_all()
        MyTNode.join_all()

        self.assertListEqual(['hello1', 'hello2'], receiver.getmsgs().split(','))

        # # send message
        # sender._send(receiver.name, "tom")
        # time.sleep(1)
        # self.assertListEqual(["tom"], receiver._receive())
        # self.assertEqual(1, receiver._nreceived)
        #
        # # send multiple
        # sender2 = MyTNode(name='sender2')
        # sender2.connect_to(receiver)
        # sender._send(receiver.name, 'tom1')
        # sender2._send(receiver.name, 'tom2')
        # self.assertListEqual(['tom1', 'tom2'], receiver._receive())
        # self.assertEqual(2, receiver._nreceived)
        #
        #

    def test_XNode(self):
        class SendNode(TNode, DummylogMixIn):
            def _work(self) -> None:
                pass

        class MiddleNode(INode, DummylogMixIn):
            def _work(self) -> None:
                pass

        class RecvNode(LNode, DummylogMixIn):
            def _work(self) -> None:
                pass

        sender1 = SendNode(name='sender1')
        sender2 = SendNode(name='sender2')
        middle = MiddleNode(name="middle")
        receiver1 = RecvNode(name='receiver1')
        receiver2 = RecvNode(name='receiver2')

        # connect and reverse connect
        sender1.connect_to(middle)
        sender2.connect_to(middle)
        middle.connect_to(receiver1)
        middle.connect_to(receiver2)
        self.assertListEqual(['middle'], sender1.downstreams)
        self.assertListEqual(['middle'], sender2.downstreams)
        self.assertListEqual(['sender1', 'sender2'], middle.upstreams)
        self.assertListEqual(['receiver1', 'receiver2'], middle.downstreams)
        self.assertListEqual(['middle'], receiver1.upstreams)
        self.assertListEqual(['middle'], receiver2.upstreams)

        # send
        sender1._send(['tom1'])
        sender2._send(['tom2'])
        self.assertListEqual(['tom1', 'tom2'], middle._receive())

        middle._send(['tom3', 'tom4'])
        self.assertListEqual(['tom3'], receiver1._receive())
        self.assertListEqual(['tom4'], receiver2._receive())
