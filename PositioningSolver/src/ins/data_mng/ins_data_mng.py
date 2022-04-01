from PositioningSolver.src.data_types.containers.Container import Container
from PositioningSolver.src.ins.data_mng.data_sim import SimulatedData


class InsDataManager(Container):
    __slots__ = ["receiver_position", "receiver_clock", "prefit_residuals",
                 "postfit_residuals", "DOPs", "estimated_iono",
                 "sat_info", "raw_obs_data", "processed_obs_data",
                 "obs_header", "nav_data",
                 "constellations", "services"]

    def __init__(self):
        super().__init__()
        self.time = SimulatedData("time", "time", "s", ...)
        self.receiver_clock = None
        self.estimated_iono = None
        self.prefit_residuals = None
        self.postfit_residuals = None
        self.DOPs = None
        self.sat_info = None
        self.raw_obs_data = None

    def __str__(self):
        return f'{type(self).__name__}( DataManager for GNSS algorithms )'

    def __repr__(self):
        return str(self)
