import tkinter as tk

from nodes.node import Node


class TKMixIn(tk.Label, Node):
    def __init__(self, **kwargs):
        __text = tk.StringVar()
        super().__init__(textvariable=__text, **kwargs)
        self.pack()
        __text.set(self.__class__.__name__)

