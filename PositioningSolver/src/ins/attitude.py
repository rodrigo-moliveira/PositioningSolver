from PositioningSolver.src.math_utils.matrix import *


def matrix_ned2body(angles):
    """
    Convert Euler angles to direction cosine matrix (DCM), that is, obtain the transformation matrix from frame n (NED)
    to frame b (Body).
    The conventional rotation sequence z-y-x is adopted.

    The DCM is a 3x3 coordinate transformation matrix from n to b. That is
        v_b  = DCM * v_n. '_b' or '_n' mean the vector 'v' is expressed in the frame b or n.

    Args:
        angles: 3x1 Euler angles, rad.
    Returns:
        dcm: 3x3 coordinate transformation matrix from n to b
    """
    # the DCM matrix is the following
    #     [          cy*cz,          cy*sz,            -sy]
    #     [ sy*sx*cz-sz*cx, sy*sx*sz+cz*cx,          cy*sx]
    #     [ sy*cx*cz+sz*sx, sy*cx*sz-cz*sx,          cy*cx]
    # where (x,y,z) are (roll,pitch,yaw), s is short for sin and c is short for cos

    dcm = np.zeros((3, 3))
    c_angle = cos(angles)
    s_angle = sin(angles)

    # dcm = rot1(angles[0]) @ rot2(angles[1]) @ rot3(angles[2])

    dcm[0, 0] = c_angle[1] * c_angle[2]
    dcm[0, 1] = c_angle[1] * s_angle[2]
    dcm[0, 2] = -s_angle[1]
    dcm[1, 0] = s_angle[0] * s_angle[1] * c_angle[2] - c_angle[0] * s_angle[2]
    dcm[1, 1] = s_angle[0] * s_angle[1] * s_angle[2] + c_angle[0] * c_angle[2]
    dcm[1, 2] = c_angle[1] * s_angle[0]
    dcm[2, 0] = s_angle[1] * c_angle[0] * c_angle[2] + s_angle[2] * s_angle[0]
    dcm[2, 1] = s_angle[1] * c_angle[0] * s_angle[2] - c_angle[2] * s_angle[0]
    dcm[2, 2] = c_angle[1] * c_angle[0]

    return dcm


def matrix_ecef2ned(lat, lon):
    """
    transformation matrix from the ECEF frame to the NED frame defined by lat and lon.
    Args:
        lat: latitude, rad
        lon: longitude, rad
    """
    # m = np.array([[-sin(lat)*cos(lon), -sin(lat)*sin(lon), cos(lat)],
    #              [-sin(lon), cos(lon), 0],
    #              [-cos(lat)*cos(lon), -cos(lat)*sin(lon), -sin(lat)]])

    return rot2(-np.pi / 2.0 - lat) @ rot3(lon)


def dcm2euler(dcm):
    """
    Convert direction cosine matrix (DCM) to Euler angles (to be exported)
    The DCM matrix rotates the frame n to the frame b according to specified rotation sequence (3-2-1 by default)
    Args:
        dcm: 3x3 coordinate transformation matrix from n to b
    Returns:
        angles: 3x1 Euler angles, rad.
    """
    # the DCM matrix is the following
    #     [          cy*cz,          cy*sz,            -sy]
    #     [ sy*sx*cz-sz*cx, sy*sx*sz+cz*cx,          cy*sx]
    #     [ sy*cx*cz+sz*sx, sy*cx*sz-cz*sx,          cy*cx]
    # where (x,y,z) are (roll,pitch,yaw), s is short for sin and c is short for cos

    yaw = np.arctan2(dcm[0, 1], dcm[0, 0])  # arctan2(cy*sz, cy*cz) <=> arctan2(sz,cz)
    pitch = np.arcsin(-dcm[0, 2])
    roll = np.arctan2(dcm[1, 2], dcm[2, 2])

    return np.array([roll, pitch, yaw])


def euler_angle_range_three_axis(angles):
    """
    Limit Euler angle range.
    For the conventional 3-2-1 three-axis rotation, the angle ranges are roll in [-pi, pi],
    pitch in [-pi/2, pi/2] and yaw [-pi, pi]
    Args:
        angles: numpy array of (3,) or (3,1)
    Returns:
        angles: 3x1 Euler angles in the correct angular range, rad
    """
    half_pi = 0.5 * np.pi

    # convert the second angle in range [-pi, pi]
    a1 = angles[0]
    a2 = angle_range_pi(angles[1])
    a3 = angles[2]

    # the second angle is not within [-pi/2, pi/2]?
    if a2 > half_pi:
        a2 = np.pi - a2
        a1 = a1 + np.pi
        a3 = a3 + np.pi
    elif a2 < -half_pi:
        a2 = -np.pi - a2
        a1 = a1 + np.pi
        a3 = a3 + np.pi

    a1 = angle_range_pi(a1)
    a3 = angle_range_pi(a3)
    return np.array([a1, a2, a3])


def angle_range_pi(x):
    """
    Limit angle range within [-pi, pi]
    Args：
        x: rad
    Return:
        equivalent angle of x, [-pi, pi], rad
    """
    # [0, 2pi]
    x = x % (2*np.pi)
    # [-pi, pi]
    if x > np.pi:
        x = x - (2*np.pi)
    return x
