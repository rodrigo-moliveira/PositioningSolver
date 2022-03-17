from ...data_types.containers.Container import Container
from PositioningSolver.src.gnss.state_space.gnss_state import PositionGNSS


class StateSpace(Container):
    pass


class SPPStateSpace(StateSpace):
    __slots__ = ["receiver_position", "receiver_clock", "iono", "ISB"]

    def __init__(self, **kwargs):
        super().__init__()

        # mandatory fields (initialized to 0)
        self.receiver_position = kwargs.get("receiver_position",
                                            PositionGNSS([0, 0, 0], "ECEF", "cartesian"))  # fallback
        self.receiver_clock = kwargs.get("receiver_clock",
                                         0)  # fallback

        # optional solve-for variables (initialized to None)
        self.ISB = kwargs.get("ISB",
                              None)  # fallback (not estimated)
        self.iono = kwargs.get("iono",
                               None)  # fallback (not estimated)

    def __str__(self):
        _str = f"receiver position = {self.receiver_position}, " \
               f"receiver clock = {self.receiver_clock}"
        if self.ISB:
            _str += f", ISB = {self.ISB}\n"
        if self.iono:
            _str += f", iono = {self.iono}\n"

        return f'{type(self).__name__}( {_str} )'

    def __repr__(self):
        return str(self)

    def __len__(self):

        # n = receiver position (3) + clock bias (1)
        n = len(self.receiver_position) + 1

        if self.iono is not None:
            n += len(self.iono)

        if self.ISB is not None:
            n += len(self.ISB)

        return n
