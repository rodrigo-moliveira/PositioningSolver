# Utility functions for the mechanization equations of the INS

import numpy as np

from PositioningSolver.src.math_utils.Constants import Constant

w_ie_e = np.array([0, 0, Constant.EARTH_ROTATION])  # in rad/s. This vector is also w_ie_i, although this is not needed


# Methods to compute angular velocities between frames e - n - b
def compute_w_en_n():
    # see https://en.wikipedia.org/wiki/Earth_radius
    #rm: meridian     radius, m
    # rn: normal     radius, m
    rm_effective = rm + pos_n[2]
    rn_effective = rn + pos_n[2]

    w_en_n[0] = vel_n[1] / rn_effective  # wN
    w_en_n[1] = -vel_n[0] / rm_effective  # wE
    w_en_n[2] = -vel_n[1] * sl / cl / rn_effective  # wD
    # NOTA: o meu h é negativo!!!


def compute_w_ie_e():
    return w_ie_e


def compute_w_ie_n(lat):
    # lat in rad
    return np.array([np.cos(lat),
                     0,
                     -np.sin(lat)]) * Constant.EARTH_ROTATION


def compute_w_nb_b():
    pass
