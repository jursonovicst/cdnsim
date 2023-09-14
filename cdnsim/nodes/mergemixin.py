from abc import ABC, abstractmethod


class MergeMixIn(ABC):
    @classmethod
    @abstractmethod
    def merge(cls, others: list):
        pass
