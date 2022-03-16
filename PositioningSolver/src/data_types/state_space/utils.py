from math import sin, cos, sinh, cosh, sqrt, atan2, asin
from numpy import sign
import numpy as np

from ...math_utils.Constants import Constant

from ...math_utils.matrix import rot3, rot1

PI = Constant.PI


def _sideral(time: float):
    """
    converts time argument to rotation angle theta (multiply with Earth rotation)
    Args:
        time (float): time in seconds
    Return:
        float : theta = Earth_rotation * time, in radians
    """
    return Constant.EARTH_ROTATION * time


def matrix_ECEF2ECI(time):
    """
    rotation matrix from ECEF frame to ECI frame given time argument
    Args:
            time (float): time argument [seconds]
        Return:
            numpy.ndarray : 3x3 rotation matrix of angle theta around the Z-axis (ECEF to ECI)
    """
    theta = _sideral(time)
    return rot3(-theta)


def M2E(e, M):
    """
    Conversion from Mean Anomaly to Eccentric anomaly, or Hyperbolic anomaly.
    **REF[6]**
    Args:
        e (float) : eccentricity
        M (float) : mean anomaly [radians]
    Return:
        float: eccentric anomaly [radian]
    """

    tol = 1e-8

    if e < 1:
        # Ellipse
        if -Constant.PI < M < 0 or M > Constant.PI:
            E = M - e
        else:
            E = M + e

        def next_E(_E, _e, _M):
            return _E + (_M - _E + _e * sin(_E)) / (1 - _e * cos(_E))

        E1 = next_E(E, e, M)
        while abs(E1 - E) >= tol:
            E = E1
            E1 = next_E(E, e, M)

        return E1
    else:
        # Hyperbolic
        if e < 1.6:
            if -Constant.PI < M < 0 or M > Constant.PI:
                H = M - e
            else:
                H = M + e
        else:
            if e < 3.6 and abs(M) > Constant.PI:
                H = M - sign(M) * e
            else:
                H = M / (e - 1)

        def next_H(_H, _e, _M):
            return _H + (_M - _e * sinh(_H) + _H) / (_e * cosh(_H) - 1)

        H1 = next_H(H, e, M)
        while abs(H1 - H) >= tol:
            H = H1
            H1 = next_H(H, e, M)

        return H1


def E2v(e, E):
    """
    Conversion from Eccentric anomaly to true anomaly
    **REF[6]**
    Args:
        e (float) : eccentricity
        E (float) : eccentric anomaly [radians]
    Return:
        float: true anomaly [radian]
    """
    cos_v = (cos(E) - e) / (1 - e * cos(E))
    sin_v = (sin(E) * sqrt(1 - e ** 2)) / (1 - e * cos(E))
    v = atan2(sin_v, cos_v) % (Constant.PI * 2)

    return v


def Geodetic2Cartesian(lat, long, h):
    """
    Convert from geodetic coordinates to cartesian coordinates. Both refer to ECEF frame
    geodetic coordinates are:
        * latitude [rad]
        * longitude [rad]
        * height [m]
    cartesian coordinates are:
        * x, y, z [m]
    Algorithm B.1.1:  From Ellipsoidal to Cartesian Coordinates from **REF[1]**


    Args:
        lat: float [rad]
        long: float [rad]
        h: float [m]
    Return:
        list : [x, y, z] [m]
    """

    a = Constant.EARTH_SEMI_MAJOR_AXIS
    e2 = Constant.EARTH_ECCENTRICITY_SQ

    # compute prime vertical radius of curvature at a given latitude for a given ellipsoid
    N = a / sqrt(1 - e2 * sin(lat) * sin(lat))

    x = (N + h) * cos(lat) * cos(long)
    y = (N + h) * cos(lat) * sin(long)
    z = ((1 - e2) * N + h) * sin(lat)

    return [x, y, z]


def Cartesian2Geodetic(x, y, z):
    """
    Convert from cartesian coordinates to geodetic coordinates. Both refer to ECEF frame
    geodetic coordinates are:
        * latitude [rad]
        * longitude [rad]
        * height [m]
    cartesian coordinates are:
        * x, y, z [m]
    Algorithm B.1.2:  From Cartesian to Ellipsoidal Coordinates from **REF[1]**


    Args:
        x: float [m]
        y: float [m]
        z: float [m]
    Return:
        list : [lat, long, h] [rad,rad,m]
    """
    e2 = Constant.EARTH_ECCENTRICITY_SQ
    a = Constant.EARTH_SEMI_MAJOR_AXIS

    # computation of longitude
    long = atan2(y, x)

    # initial value of latitude
    p = sqrt(x * x + y * y)
    lat = 0 if p == 0 else atan2(z / p, 1 - e2)

    # iterative process to refine latitude
    MAX_ITERS = 10
    i = 0
    h = 0
    while i < MAX_ITERS:
        lat_prev = lat

        N = a / sqrt(1 - e2 * sin(lat) * sin(lat))
        h = p / cos(lat) - N
        lat = 0 if p == 0 else atan2(z / p, 1 - N / (N + h) * e2)

        i += 1
        if abs(lat - lat_prev) < 1E-10:
            break

    return [lat, long, h]


def ENU2ECEF(x_enu, y_enu, z_enu, lat, long, h):
    """
    Convert from ENU frame to ECEF frame (cartesian coordinates). The ENU frame is centered (origin O) at the ground
    observer (for example, the GNSS receiver)
    ENU stands for East North Up -> local components from the origin O to the satellite

    Algorithm B.2.1:  From ENU to ECEF Coordinates from **REF[1]**

    Args:
        x_enu: float [m]
        y_enu: float [m]
        z_enu: float [m]
        lat: float -> latitude of ground observer [rad]
        long: float -> longitude of ground observer [rad]
        h: float -> height of ground observer [m]
    Return:
        list : [x_ecef, y_ecef, z_ecef]  [m]
    """
    # get rotation matrix from ENU to ECEF
    R = rot3(-(PI / 2 + long)) @ rot1(-(PI / 2 - lat))

    # ECEF coordinates of ENU origin
    [x_or, y_or, z_or] = Geodetic2Cartesian(lat, long, h)

    # apply transform
    x, y, z = np.array([x_or, y_or, z_or]) + R @ np.array([x_enu, y_enu, z_enu])

    return [x, y, z]


def ECEF2ENU(x_ecef, y_ecef, z_ecef, lat, long, h):
    """
    Convert from ECEF frame to ENU frame (cartesian coordinates). The ENU frame is centered (origin O) at the ground
    observer (for example, the GNSS receiver)
    ENU stands for East North Up -> local components from the origin O to the satellite

    Algorithm B.2.2:  From ECEF to ENU Coordinates from **REF[1]**

    Args:
        x_ecef (float) : [m]
        y_ecef (float) : [m]
        z_ecef (float) : [m]
        lat (float) : latitude of ground observer [rad]
        long (float) : longitude of ground observer [rad]
        h (float) : height of ground observer [m]
    Return:
        list : [x_enu, y_enu, z_enu]  [m]
    """
    # get rotation matrix from ENU to ECEF
    R = rot1((PI / 2 - lat)) @ rot3((PI / 2 + long))

    # ECEF coordinates of ENU origin (ground receiver)
    x_or, y_or, z_or = Geodetic2Cartesian(lat, long, h)

    # apply transform
    x, y, z = R @ np.array([x_ecef - x_or,
                            y_ecef - y_or,
                            z_ecef - z_or])

    return [x, y, z]


def ENU2AzEl(x_enu, y_enu, z_enu):
    """
    Transform ENU coordinates in Azimuth (Az) and Elevation (El) observation angles
    Algorithm B.3:  Elevation and Azimuth Computation from **REF[1]**

    Args:
        x_enu : float [m]
        y_enu : float [m]
        z_enu : float [m]
    Return:
        list : [Az, El] [rad]
    """
    dist = sqrt(x_enu*x_enu + y_enu*y_enu + z_enu*z_enu)

    El = asin(z_enu / dist)

    Az = atan2(x_enu, y_enu) % (2 * PI)

    return [Az, El]
