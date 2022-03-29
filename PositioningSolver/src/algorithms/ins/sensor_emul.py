# Emulate IMU (compute true readouts and corrupt them with noise)

import numpy as np

from PositioningSolver.src.ins.attitude import matrix_ned2body, matrix_ecef2ned
from PositioningSolver.src.ins.mechanization import compute_w_nb_b
from PositioningSolver.src.math_utils.finite_diff import finite_difference
from PositioningSolver.src.math_utils.matrix import vector2skew_symmetric


def imu_emulation(time, position, velocity, attitude):

    # gyro is w_ib_b
    # accel is f_ib_b

    # iterate in vectors
    for i in range(1, len(time)):

        # 1 - unpack data for this epoch
        t = time[i]
        lla = position[i]
        v_eb_n = velocity[i]
        euler = attitude[i]
        step = t - time[i-1]

        # 2 - compute rotation matrices
        c_nb = matrix_ned2body(euler)  # matrix from n to b
        c_en = matrix_ecef2ned(lla[0], lla[1])  # matrix from e to n
        c_bn = c_nb.T

        # 3 - apply finite differences to euler angles
        euler_dot = finite_difference(attitude[i-1], euler, step)

        # 4 - apply finite differences to velocity vector
        vel_dot = finite_difference(velocity[i-1], v_eb_n, step)  # v_eb_n dot

        # 5 - apply mechanization equation
        w_nb_b = compute_w_nb_b(euler_dot, euler)

        v_eb_b = c_nb @ v_eb_n
        v_eb_b_dot = c_nb @ vel_dot - np.cross(w_nb_b, v_eb_b)

        att = np.array([0.00000000e+00, 2.53143332e+00, -6.06927082e-05 ])
        att_dot = np.array([0, -0.50436764,  0 ])
        print(compute_w_nb_b(att_dot, att))
        exit()

# TODO: passar esta função para o ficheiro mechanization
def true_imu_output(pos_n, vel_b, att, c_nb, vel_dot_b, att_dot, ref_frame, g):
    """
    Calculate true IMU results from attitude change rate and velocity
    change rate.
    attitude change rate is input in the form of Euler angle derivatives and
    converted into angular velocity. Velocity change rate is expressed in
    the body frame. Position change rate is also calculated. If simulation is
    done in the NED frame, the position change rate is in the form of Lat, Lon
    and alt derivatives. Otherwise, it is given in m/s.
    Args:
        pos_n: For NED, it is the absolute LLA position. Otherwise, it is relative
            motion.
        vel_b: Velocity in the body frame, m/s.
        att: Euler angles, [yaw pitch roll], rot seq is ZYX, rad.
        c_nb: Transformation matrix from b to n corresponding to att.
        vel_dot_b: Velocity change rate in the body frame, m/s/s
        att_dot: Euler angle change rate, [yaw_d, pitch_d, roll_d], rad/s
        ref_frame: See doc of function PathGen.
        g: Gravity, only used when ref_frame==1, m/s/s.
    Returns:
        [0]: 3x1 true accelerometer output in the body frame, m/s/s
        [1]: 3x1 true gyro output in the body frame, rad/s
        [2]: 3x1 velocity change rate in the navigation frame, m/s/s
        [3]: 3x1 position change rate in the navigation frame, m/s
    """
    # velocity in N
    vel_n = c_nb.dot(vel_b)

    # Calculate rotation rate of n w.r.t e in n and e w.r.t i in n
    # For the NED frame, the NED frame rotation and Earth rotation rate is calculated
    # For the virtual inertial frame, they are not needed and simply set to zeros.
    w_en_n = np.zeros(3)
    w_ie_n = np.zeros(3)
    if ref_frame == 0:
        earth_param = geoparams.geo_param(pos_n)
        rm = earth_param[0]
        rn = earth_param[1]
        g = earth_param[2]
        sl = earth_param[3]
        cl = earth_param[4]
        w_ie = earth_param[5]
        rm_effective = rm + pos_n[2]
        rn_effective = rn + pos_n[2]
        gravity = np.array([0, 0, g])
        w_en_n[0] = vel_n[1] / rn_effective              # wN
        w_en_n[1] = -vel_n[0] / rm_effective             # wE
        w_en_n[2] = -vel_n[1] * sl /cl / rn_effective    # wD
        w_ie_n[0] = w_ie * cl
        w_ie_n[2] = -w_ie * sl
    else:
        gravity = [0, 0, g]

    # Calculate rotation rate of b w.r.t n expressed in n.
    # Calculate rotation rate from Euler angle derivative using ZYX rot seq.
    sh = math.sin(att[0])
    ch = math.cos(att[0])
    w_nb_n = np.zeros(3)
    w_nb_n[0] = -sh*att_dot[1] + c_nb[0, 0]*att_dot[2]
    w_nb_n[1] = ch*att_dot[1] + c_nb[1, 0]*att_dot[2]
    w_nb_n[2] = att_dot[0] + c_nb[2, 0]*att_dot[2]
    # Calculate rotation rate from rotation quaternion
    # w_nb_n = np.zeros(3)

    # Velocity derivative
    vel_dot_n = c_nb.dot(vel_dot_b) + attitude.cross3(w_nb_n, vel_n)
    # Position derivative
    pos_dot_n = np.zeros(3)
    if ref_frame == 0:
        pos_dot_n[0] = vel_n[0] / rm_effective      # Lat
        pos_dot_n[1] = vel_n[1] / rn_effective / cl # Lon
        pos_dot_n[2] = -vel_n[2]                    # Alt
    else:
        pos_dot_n[0] = vel_n[0]
        pos_dot_n[1] = vel_n[1]
        pos_dot_n[2] = vel_n[2]
    # Gyroscope output
    gyro = c_nb.T.dot(w_nb_n + w_en_n + w_ie_n)
    # Acceleration output
    w_ie_b = c_nb.T.dot(w_ie_n)
    acc = vel_dot_b + attitude.cross3(w_ie_b+gyro, vel_b) - c_nb.T.dot(gravity)
    return acc, gyro, vel_dot_n, pos_dot_n