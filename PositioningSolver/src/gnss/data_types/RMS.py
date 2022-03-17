import numpy as np

from PositioningSolver.src.data_types.containers.Container import Container
from PositioningSolver.src.data_types.containers.TimeSeries import TimeSeries
from PositioningSolver.src.quality_check.rms_manager import compute_error_static, compute_RMS_stats_static


class _RMS(Container):
    """
    class for time series RMS for each component (x, y, z)
    """

    __slots__ = ["x", "y", "z", "norm"]

    def __init__(self):
        super().__init__()
        self.x = None
        self.y = None
        self.z = None


class RMS(TimeSeries):
    def __init__(self):
        super().__init__()
        self.stats = {}  # dict with time averaged RMS. keys are {"x", "y", "z", "2D", "3D"}
        self._absolute_error = TimeSeries()

    def compute_errors(self, receiver_pos, true_pos, mode, frame="ECEF"):
        if mode == "static":
            compute_error_static(self, receiver_pos, true_pos, frame)
            self.stats = compute_RMS_stats_static(self)
        else:
            raise AttributeError(f"In the current software version only 'static' mode is permitted")

    def set_rms_data(self, epoch, error):
        rms = _RMS()
        rms.x = error[0]
        rms.y = error[1]
        rms.z = error[2]
        rms.norm = np.linalg.norm(error)

        self.set_data(epoch, rms)

    def export2time_data(self, norm=False):
        self.sort()
        t = list(self.keys())
        x = [err.x for err in self.values()]
        y = [err.y for err in self.values()]
        z = [err.z for err in self.values()]

        if not norm:
            return t, x, y, z

        _norm = [err.norm for err in self.values()]
        return t, x, y, z, _norm
