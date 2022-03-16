from PositioningSolver.src.data_types.state_space.utils import Geodetic2Cartesian, Cartesian2Geodetic


def ecef2lla(data):
    _time, _len = data.shape

    for t in range(_time):
        data[t, :] = Cartesian2Geodetic(*data[t, :])


def lla2ecef(data):
    _time, _len = data.shape

    for t in range(_time):
        data[t, :] = Geodetic2Cartesian(*data[t, :])