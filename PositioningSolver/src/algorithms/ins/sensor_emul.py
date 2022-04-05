# Emulate IMU (compute true readouts and corrupt them with noise)

import numpy as np

from PositioningSolver.src.algorithms.ins.ins_alg import InsAlgorithm
from PositioningSolver.src.ins.mechanization.attitude import matrix_ned2body, matrix_ecef2ned
from PositioningSolver.src.ins.mechanization.gravity import acceleration, lla2ecef
from PositioningSolver.src.math_utils.finite_diff import finite_difference
from PositioningSolver.src.ins import mechanization


# funçaõ imu_emulation que recebe true PVAT, data_manager e modelo de IMU
# calcula true readouts
# corrompe com ruido em funcao do IMU dado
# guarda para o datamanager

# funcao gps_emulation que recebe true PVAT, datamanager e modelo de GPS, ...
#...
#...

class SensorEmulationAlg(InsAlgorithm):
    def __init__(self):
        pass

    def compute(self, time, position, velocity_n, attitude):
        # n-frame mechanization

        # initialize outputs

        w_ib_b = np.zeros((len(time), 3))  # gyro is w_ib_b
        f_ib_b = np.zeros((len(time), 3))  # accel is f_ib_b

        # iterate in time
        for i in range(1, len(time)):

            # 1 - unpack data for this epoch
            t = time[i]
            lla = position[i]  # remember that altitude is positive downwards!
            v_eb_n = velocity_n[i]
            euler = attitude[i]
            step = t - time[i-1]

            # 2 - compute rotation matrices
            c_nb = matrix_ned2body(euler)  # matrix from n to b
            c_en = matrix_ecef2ned(lla[0], lla[1])  # matrix from e to n

            # 3 - apply finite differences to euler angles
            euler_dot = finite_difference(attitude[i-1], euler, step)

            # 4 - apply finite differences to velocity vector (in n frame!)
            v_eb_n_dot = finite_difference(velocity_n[i-1], v_eb_n, step)

            # 5 - get rotation vectors between frames i-e, e-n and n-b, and local gravity vector
            w_nb_b = mechanization.compute_w_nb_b(euler_dot, euler)
            w_ie_n = mechanization.compute_w_ie_n(lla[0])
            w_en_n = mechanization.compute_w_en_n(v_eb_n, lla)
            r_eb_e = lla2ecef(lla)
            g_eb_e = acceleration(r_eb_e)

            # 6 - finally, apply the mechanization equations (in the n-frame)
            w_ib_b[i] = mechanization.compute_w_ib_b(c_nb, w_ie_n, w_en_n, w_nb_b)
            f_ib_b[i] = mechanization.compute_f_ib_b(c_nb, c_en, w_en_n, w_ie_n, v_eb_n_dot, g_eb_e, v_eb_n)

        return w_ib_b, f_ib_b
