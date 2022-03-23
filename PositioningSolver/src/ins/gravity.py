import numpy as np

from PositioningSolver.src.gnss.state_space.utils import Cartesian2Geodetic, Geodetic2Cartesian
from PositioningSolver.src.math_utils.Constants import Constant

# Constants
MU = Constant.MU
FLATTENING = Constant.EARTH_FLATNESS
a = Constant.EARTH_SEMI_MAJOR_AXIS
e_sq = Constant.EARTH_ECCENTRICITY_SQ


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


def geo_param(pos):
    """
    Calculate local radius and gravity given the [Lat, Lon, Alt]
    Local radius include meridian radius rm and normal radius rn.
    Args:
        pos: [Lat, Lon, Alt], rad, m
    Returns:
        rm: meridian radius, m
        rn: normal radius, m
        g: gravity w.r.t Earth frame, m/s/s
        sl: sin(Lat)
        cl: cos(lat)
        w_ie: Earth's rotation rate w.r.t the inertial frame, rad/s
    """
    # some constants
    normal_gravity = 9.7803253359
    k = 0.00193185265241        # WGS-84 gravity model constant. For more details, refer to
                                # https://en.wikipedia.org/wiki/Gravity_of_Earth
    m = 0.00344978650684        # m = w*w*a*a*b/GM
    # calc
    sl = np.sin(pos[0])
    cl = np.cos(pos[0])
    sl_sqr = sl * sl
    h = pos[2]

    g1 = normal_gravity * (1 + k*sl_sqr) / np.sqrt(1.0 - e_sq*sl_sqr)
    g = g1 * (1.0 - (2.0/a) * (1.0 + FLATTENING + m - 2.0*FLATTENING*sl_sqr)*h + 3.0*h*h/a/a)
    return g, sl, cl


def get_earth_radii(lat):
    # Eq. 6 of Sensors 2012, 12 (see paper full name...)
    # see https://en.wikipedia.org/wiki/Earth_radius section 'Radii of curvature'
    # Rn -> primer vertical at provided latitude
    # Rm -> Radius of curvature in the meridian

    sl_sqr = np.sin(lat)**2

    rm = (a * (1 - e_sq)) / (np.sqrt(1.0 - e_sq * sl_sqr) * (1.0 - e_sq * sl_sqr))
    rn = a / (np.sqrt(1.0 - e_sq * sl_sqr))

    return rm, rn


def acceleration(r_eb_e, mode="earth"):
    """
    compute acceleration due to zonal harmonics.
    The harmonics coded are the low-order ones (the equations are hard-coded) and
    the general harmonic series is not applied

    Args:
        ----------
        r_eb_e : numpy array of (3,) or (3,1)
            position vector in expressed e-frame coordinates
        mode : str
            'inertial' to compute inertial gravity or 'earth' to compute gravity w.r.t. Earth (Coriolis effect)

    NOTE: The relation between inertial gravity and gravity w.r.t. Earth is given by:
        Earth_grav^e = Inertial_grav^e - w_ie_e x (w_ie_e x r_eb_e)

    where
        w_ie_e x (w_ie_e x r_eb_e) = [-w_Earth^2 . x, -w_Earth^2 . y, 0]^T

    Returns:
        numpy array of (3,)
            g_eb^e if mode = 'earth' (gravity w.r.t Earth in e-frame coordinates)
            g_ib^e if mode = 'inertial' (inertial gravity in e-frame coordinates)
    """

    if mode not in ["earth", "inertial"]:
        raise TypeError(f"Invalid argument 'mode'. Must either be 'earth' or 'inertial'")

    if mode == "earth":
        w_2 = Constant.EARTH_ROTATION**2
    else:
        w_2 = 0
    x, y, z = r_eb_e

    R = np.linalg.norm(r_eb_e)
    r_2 = R * R

    a = -MU * r_eb_e / (R ** 3)

    aux = -3 * Constant.EARTH_J2 * MU * Constant.EARTH_SEMI_MAJOR_AXIS ** 2 / (2 * R ** 5)
    aux1 = aux * (1 - 5 * z ** 2 / r_2) * x
    a[0] = w_2 * x + a[0] + aux1
    a[1] = w_2 * y + a[1] + aux1 * y / x
    a[2] = a[2] + aux * (3 - 5 * z ** 2 / r_2) * z

    return a
