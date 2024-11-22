from cdnsim.arrival import Arrival


class Constant(Arrival):
    """
    Constant arrival process. *rate* number of arrivals in every tick.
    """

    def __init__(self, rate: float, **kwargs):
        super().__init__(**kwargs)
        self.__rate = rate

    def __next__(self) -> int:
        super().__next__()
        return int(self.__rate)
