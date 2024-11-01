from abc import ABC, abstractmethod


class GuiMixIn(ABC):

    @classmethod
    @abstractmethod
    def initialize(cls):
        ...

    @classmethod
    @abstractmethod
    def destroy(cls):
        ...
