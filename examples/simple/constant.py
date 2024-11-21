from cdnsim.arrival import Arrival


class Constant(Arrival):
    """
    Constant arrival process. *rate* number of arrival in every tick.
    """
    def __init__(self, rate: float, ticks: int, **kwargs):
        super().__init__(**kwargs)
        self.__rate = rate
        self.__ticks = ticks

    def __next__(self) -> int:
        print(f"IIIIII {self.__ticks}")
        if self.__ticks <= 0:
            raise StopIteration
        self.__ticks -= 1
        return int(self.__rate*2)
