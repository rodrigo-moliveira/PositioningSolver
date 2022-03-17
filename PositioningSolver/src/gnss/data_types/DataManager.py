from PositioningSolver.src.gnss.data_types.NavigationData import NavigationDataMap
from PositioningSolver.src.data_types.containers.Container import Container
from PositioningSolver.src.gnss.data_types.ObservationData import ObservationHeader, ObservationData
from PositioningSolver.src.data_types.containers.TimeSeries import TimeSeries
from PositioningSolver.src.gnss.data_types.DOP import DOP
from PositioningSolver.src.gnss.data_types.ServiceManager import ServiceManager


class GNSSDataManager(Container):
    __slots__ = ["receiver_position", "receiver_clock", "prefit_residuals",
                 "postfit_residuals", "DOPs", "estimated_iono",
                 "sat_info", "raw_obs_data", "processed_obs_data",
                 "obs_header", "nav_data",
                 "constellations", "services"]

    def __init__(self):
        super().__init__()
        self.receiver_position = TimeSeries()
        self.receiver_clock = TimeSeries()
        self.estimated_iono = TimeSeries()
        self.prefit_residuals = TimeSeries()
        self.postfit_residuals = TimeSeries()
        self.DOPs = DOP()
        self.sat_info = TimeSeries()
        self.raw_obs_data = ObservationData()
        self.processed_obs_data = None
        self.obs_header = ObservationHeader()
        self.nav_data = NavigationDataMap()
        self.constellations = []
        self.services = ServiceManager()

    def __str__(self):
        return f'{type(self).__name__}( DataManager for GNSS algorithms )'

    def __repr__(self):
        return str(self)

    def set_constellation(self, constellation, observations):
        self.constellations.append(constellation)
        self.services.add_service(constellation, observations)

    def get_constellations(self):
        return self.constellations
