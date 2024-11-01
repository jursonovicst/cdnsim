import numpy as np

from cdnsim_old.content import ContentMixIn
from cdnsim_old.content import Obj


class ZipfMixIn(ContentMixIn):
    """
    Implements a zipf distribution based content base.
    """

    def __init__(self, alpha: float, **kwargs):
        super().__init__(**kwargs)
        self.__alpha = alpha
        self.__n = len(self._content_base)
        self.__generator = np.random.Generator(np.random.PCG64())

    def _content(self, size: int) -> list[Obj]:
        return [self._content_base[min(k, self.__n) - 1] for k in self.__generator.zipf(self.__alpha, size)]
