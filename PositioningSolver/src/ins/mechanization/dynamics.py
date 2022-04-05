import numpy as np

from PositioningSolver.src.ins.mechanization.attitude import matrix_ned2body, matrix_ecef2ned


def velE2velN(v_eb_e, lld):
    """
    convert ecef velocity written in ecef components, v_eb_e, to navigation frame (NED) components, v_eb_n
    For that we apply the rotation
        v_eb_n = c_en @ v_eb_e
    where c_en is the rotation matrix from ecef (e) to ned (n)
    """
    v_eb_n = np.zeros(v_eb_e.shape)

    for i in range(v_eb_e.shape[0]):
        c_en = matrix_ecef2ned(lld[i, 0], lld[i, 1])
        v_eb_n[i] = c_en @ v_eb_e[i]

    return v_eb_n


def velB2velN(v_eb_b, angles):
    """
    convert ecef velocity written in body components, v_eb_b, to navigation frame (NED) components, v_eb_n
    For that we apply the rotation
        v_eb_n = c_bn @ v_eb_b
    where c_bn is the rotation matrix from body (b) to ned (n)
    """
    v_eb_n = np.zeros(v_eb_b.shape)

    for i in range(v_eb_b.shape[0]):
        c_bn = matrix_ned2body(angles[i]).T
        v_eb_n[i] = c_bn @ v_eb_b[i]

    return v_eb_n
