import multiprocessing as mp
from pathlib import Path
from unittest import TestCase

from nodes.log import DummylogMixIn
from nodes.node import Node, LNode, TNode, XNode, YNode


class MyNode(Node, DummylogMixIn):
    def _work(self) -> None:
        Path('_out/test.txt').touch()


class MyTNode(TNode, DummylogMixIn):
    """
    Sends one *msg* message, then terminates
    """

    def __init__(self, msg: str, **kwargs):
        super().__init__(**kwargs, args=(msg,))

    def _work(self, msg) -> None:
        for to in self.remotes:
            self._send(to, msg)
        self._terminate()


class MyLNode(LNode, DummylogMixIn):
    """
    Receives messages.
    """

    def __init__(self, **kwargs):
        self._array = mp.Array('c', 256)

        super().__init__(**kwargs, args=(self._array,))

    def _work(self, array) -> None:
        while msgs := self._receive():
            array.value = ','.join([msg for msg in msgs]).encode('ASCII')

    def getmsgs(self) -> str:
        return self._array.value.decode('ASCII')


class TestNode(TestCase):
    def setUp(self) -> None:
        Node.terminate_all()

    def tearDown(self) -> None:
        Node.terminate_all()

    def test_node(self):
        # simplest node implementation
        node1 = MyNode()
        self.assertTrue(node1.name.startswith("MyNode-"))
        self.assertEqual(1, len(Node.list_all()))
        self.assertTrue(Node.list_all()[0].name.startswith("MyNode-"))

        # check work function
        Path('_out/test.txt').unlink(missing_ok=True)
        MyNode.start_all()
        MyNode.join_all()
        self.assertEqual(1, len(Node.list_all()), "tpm")
        self.assertTrue(Path('_out/test.txt').exists())

        MyNode.terminate_all()
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
        self.assertEqual(0, len(sender1.remotes))

        # connect node
        sender1.connect_to(receiver)
        sender2.connect_to(receiver)
        self.assertListEqual([receiver.name], sender1.remotes)
        self.assertListEqual([receiver.name], sender2.remotes)

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

        class MiddleNode(XNode, DummylogMixIn):
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
        self.assertListEqual(['middle'], sender1.remotes)
        self.assertListEqual(['middle'], sender2.remotes)
        self.assertListEqual(['receiver1', 'receiver2'], middle.remotes)

        # send
        sender1._send(middle.name, 'tom1')
        sender2._send(middle.name, 'tom2')
        self.assertListEqual(['tom1', 'tom2'], middle._receive())

        middle._send(receiver1.name, 'tom3')
        middle._send(receiver2.name, 'tom4')
        self.assertListEqual(['tom3'], receiver1._receive())
        self.assertListEqual(['tom4'], receiver2._receive())

    def test_YNode(self):
        class SendNode(TNode, DummylogMixIn):
            def _work(self) -> None:
                pass

        class MiddleNode(YNode, DummylogMixIn):
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
        with self.assertRaises(SyntaxError):
            middle.connect_to(receiver2)
        self.assertListEqual(['middle'], sender1.remotes)
        self.assertListEqual(['middle'], sender2.remotes)
        self.assertListEqual(['receiver1'], middle.remotes)

        # send
        sender1._send(middle.name, 'tom1')
        sender2._send(middle.name, 'tom2')
        self.assertListEqual(['tom1', 'tom2'], middle._receive())

        middle._send(receiver1.name, 'tom3')
        self.assertListEqual(['tom3'], receiver1._receive())
