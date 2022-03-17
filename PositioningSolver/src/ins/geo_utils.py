import numpy as np

from PositioningSolver.src.gnss.state_space.utils import Cartesian2Geodetic, Geodetic2Cartesian


def ecef2lla(data):
    _time, _len = data.shape
    lla = np.zeros((_time, _len))

    for t in range(_time):
        lla[t, :] = Cartesian2Geodetic(*data[t, :])

    return lla


def lla2ecef(data):
    _time, _len = data.shape
    ecef = np.zeros((_time, _len))

    for t in range(_time):
        ecef[t, :] = Geodetic2Cartesian(*data[t, :])

    return ecef
