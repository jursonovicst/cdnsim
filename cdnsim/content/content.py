from abc import ABC, abstractmethod

from cdnsim.content import Obj


class ContentMixIn(ABC):

    def __init__(self, content_base: list[Obj], **kwargs):
        self._content_base = content_base
        super().__init__(**kwargs)


    @abstractmethod
    def _content(self, size: int) -> list[Obj]:
        """
        Implement this to draw requests from the content base.
        :return: ndarray of content
        """
        ...
