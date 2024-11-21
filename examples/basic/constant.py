from cdnsim.arrival import Arrival


class Constant(Arrival):
    """
    Constant arrival process. *rate* number of arrival in every tick.
    """

    def __init__(self, rate: float, ticks: int, **kwargs):
        super().__init__(**kwargs)
        self.__rate = rate
        self.__ticks = ticks

    def __iter__(self):
        self.__tick = self.__ticks
        return self

    def __next__(self) -> int:
        if self.__tick <= 0:
            raise StopIteration
        self.__tick -= 1
        return int(self.__rate)
