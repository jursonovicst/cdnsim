from cdnsim.arrival import Arrival


class Constant(Arrival):
    """
    Constant arrival process. *rate* number of arrival in every tick.
    """

    def __init__(self, rate: float, **kwargs):
        super().__init__(**kwargs)
        self.__rate = rate

    def __next__(self) -> int:
        if self._tick <= 0:
            raise StopIteration
        self._tick -= 1
        return int(self.__rate)
