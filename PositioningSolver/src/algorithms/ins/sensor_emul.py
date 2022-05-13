# Emulate IMU (compute true readouts and corrupt them with noise)

import numpy as np

from PositioningSolver.src.algorithms.ins.ins_alg import InsAlgorithm
from PositioningSolver.src.ins import mechanization
from PositioningSolver.src.math_utils.finite_diff import finite_difference



# funçaõ imu_emulation que recebe true PVAT, data_manager e modelo de IMU
# calcula true readouts
# corrompe com ruido em funcao do IMU dado
# guarda para o datamanager

# funcao gps_emulation que recebe true PVAT, datamanager e modelo de GPS, ...
#...
# ...


class SensorEmulationAlg(InsAlgorithm):
    def __init__(self, imu, gps):
        super().__init__()
        self.inputs = ["time", "ref_pos", "ref_vel", "ref_att"]
        self.outputs = ["ref_gyro", "ref_accel", "gyro", "accel", "gps"]
        self.imu = imu
        self.gps = gps

    def __str__(self):
        return "InsAlgorithm(Sensor Emulation Algorithm)"

    def compute(self, time, pos_lld, vel_eb_n, euler_att):
        true_gyro, true_accel = self._compute_true_imu_readouts(time, pos_lld, vel_eb_n, euler_att)
        sampling_time = float(time[1] - time[0])

        # compute error readouts
        self._corrupt_noise_imu(true_gyro, true_accel, sampling_time)
        # self._corrupt_noise_gps(pos_lld, vel_eb_n, euler_att)

        # add to outputs
        # self.results.append(None)
        # self.results.append(None)

    def _corrupt_noise_imu(self, true_gyro, true_accel, sampling_time):
        for sensor, true_readouts in zip(["gyroscope", "accelerometer"], [true_gyro, true_accel]):
            readout = self._add_errors_imu(sensor, true_readouts, sampling_time)

            self.results.append(readout)

    def _add_errors_imu(self, sensor, true_readouts, sampling_time):
        user_models = self.imu[sensor]

        # TODO missing misalignment and scale_factor
        misalignment = user_models["misalignment"].get_stochastic_process(len(true_readouts)).compute(sampling_time)
        scale_factor = user_models["scale_factor"].get_stochastic_process(len(true_readouts)).compute(sampling_time)
        bias_constant = user_models["bias_constant"].get_stochastic_process(len(true_readouts)).compute(sampling_time)
        bias_drift = user_models["bias_drift"].get_stochastic_process(len(true_readouts)).compute(sampling_time)
        noise = user_models["observation_noise"].get_stochastic_process(len(true_readouts)).compute(sampling_time)
        print(np.shape(true_readouts), np.shape(bias_constant), np.shape(bias_drift), np.shape(noise))
        readout = true_readouts + bias_drift + bias_constant + noise

        return readout



    def _compute_true_imu_readouts(self, time, pos_lld, vel_eb_n, euler_att):
        # n-frame mechanization

        # initialize outputs

        w_ib_b = np.zeros((len(time), 3))  # gyro is w_ib_b
        f_ib_b = np.zeros((len(time), 3))  # accel is f_ib_b

        # iterate in time
        for i in range(1, len(time)):

            # 1 - unpack data for this epoch
            t = time[i, 0]
            lld = pos_lld[i]  # remember that altitude is positive downwards!
            v_eb_n = vel_eb_n[i]
            euler = euler_att[i]
            step = t - time[i-1, 0]

            # 2 - compute rotation matrices
            c_nb = mechanization.matrix_ned2body(euler)  # matrix from n to b
            c_en = mechanization.matrix_ecef2ned(lld[0], lld[1])  # matrix from e to n

            # 3 - apply finite differences to euler angles
            euler_dot = finite_difference(euler_att[i-1], euler, step)

            # 4 - apply finite differences to velocity vector (in n frame!)
            v_eb_n_dot = finite_difference(vel_eb_n[i-1], v_eb_n, step)

            # 5 - get rotation vectors between frames i-e, e-n and n-b, and local gravity vector
            w_nb_b = mechanization.compute_w_nb_b(euler_dot, euler)
            w_ie_n = mechanization.compute_w_ie_n(lld[0])
            w_en_n = mechanization.compute_w_en_n(v_eb_n, lld)
            r_eb_e = mechanization.lld2ecef(lld)
            g_eb_e = mechanization.grav_acceleration(r_eb_e)

            # 6 - finally, apply the mechanization equations (in the n-frame)
            w_ib_b[i] = mechanization.compute_w_ib_b(c_nb, w_ie_n, w_en_n, w_nb_b)
            f_ib_b[i] = mechanization.compute_f_ib_b(c_nb, c_en, w_en_n, w_ie_n, v_eb_n_dot, g_eb_e, v_eb_n)

        # append to results
        self.results.append(w_ib_b)
        self.results.append(f_ib_b)

        return w_ib_b, f_ib_b
