import numpy as np

from PositioningSolver.src.data_types.basics.Epoch import Epoch
from PositioningSolver.src.data_types.containers.Container import Container
from PositioningSolver.src.data_types.containers.TimeSeries import TimeSeries
from PositioningSolver.src.math_utils.Constants import Constant
from PositioningSolver.src.math_utils.matrix import rot1, rot3


class _DOP(Container):
    """
    available DOPs are:
    matrix, geometry, position, time, horizontal, x_ecef, y_ecef, z_ecef, north, east, up
    """

    __slots__ = ["matrix", "geometry", "position",
                 "time", "horizontal",
                 "x_ecef", "y_ecef", "z_ecef", "east", "north", "up"]

    def __init__(self):
        super().__init__()
        self.matrix = None
        self.geometry = None
        self.position = None
        self.time = None
        self.horizontal = None
        self.x_ecef = None
        self.y_ecef = None
        self.z_ecef = None
        self.north = None
        self.east = None
        self.up = None


class DOP(TimeSeries):

    def __init__(self):
        super().__init__()

    def set_dop(self, epoch: Epoch, dop_type, dop_value):

        if not isinstance(epoch, Epoch):
            raise TypeError(f'First argument should be a valid Epoch object. Type {type(epoch)} was provided instead')

        if not self.has_epoch(epoch):
            self.set_data(epoch, _DOP())

        setattr(self.get_data_for_epoch(epoch), dop_type, dop_value)

    def compute_DOPs(self, receiver_pos: TimeSeries):

        for epoch, DOPs in self.items():
            # get receiver position
            receiver = receiver_pos.get_data_for_epoch(epoch).copy()
            receiver.form = "geodetic"
            lat, long, h = receiver

            # get ECEF DOP matrix
            DOP_matrix = DOPs.matrix

            # geometry DOP
            DOPs.geometry = np.sqrt(DOP_matrix[0, 0] + DOP_matrix[1, 1] + DOP_matrix[2, 2] + DOP_matrix[3, 3])

            # position DOP
            DOPs.position = np.sqrt(DOP_matrix[0, 0] + DOP_matrix[1, 1] + DOP_matrix[2, 2])

            # time DOP
            DOPs.time = np.sqrt(DOP_matrix[3, 3])

            # x, y, z DOPs
            DOPs.x_ecef = np.sqrt(DOP_matrix[0, 0])
            DOPs.y_ecef = np.sqrt(DOP_matrix[1, 1])
            DOPs.z_ecef = np.sqrt(DOP_matrix[2, 2])

            # get DOPs with respect to ENU coordinates
            R = rot1((Constant.PI / 2 - lat)) @ rot3((Constant.PI / 2 + long))  # rotation matrix from ECEF to ENU
            DOP_ENU = R @ DOP_matrix[0:3, 0:3] @ R.T

            # east, north, up DOPs
            DOPs.east = np.sqrt(DOP_ENU[0, 0])
            DOPs.north = np.sqrt(DOP_ENU[1, 1])
            DOPs.up = np.sqrt(DOP_ENU[2, 2])

            # horizontal DOP
            DOPs.horizontal = np.sqrt(DOP_ENU[0, 0] + DOP_ENU[1, 1])

    def export2time_data(self):
        self.sort()
        t = list(self.keys())
        matrix = [_dop.matrix for _dop in self.values()]
        geometry = [_dop.geometry for _dop in self.values()]
        position = [_dop.position for _dop in self.values()]
        time = [_dop.time for _dop in self.values()]
        horizontal = [_dop.horizontal for _dop in self.values()]

        x = [_dop.x_ecef for _dop in self.values()]
        y = [_dop.y_ecef for _dop in self.values()]
        z = [_dop.z_ecef for _dop in self.values()]

        east = [_dop.east for _dop in self.values()]
        north = [_dop.north for _dop in self.values()]
        up = [_dop.up for _dop in self.values()]

        return t, matrix, geometry, position, time, horizontal, x, y, z, east, north, up
