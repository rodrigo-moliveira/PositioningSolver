# Emulate IMU (compute true readouts and corrupt them with noise)

import numpy as np

from PositioningSolver.src.algorithms.ins.ins_alg import InsAlgorithm
from PositioningSolver.src.ins import mechanization
from PositioningSolver.src.ins.mechanization import lld2ecef, matrix_ecef2ned, ecef2lld
from PositioningSolver.src.math_utils.finite_diff import finite_difference
from PositioningSolver.src.math_utils.matrix import rot1, rot2, rot3


class SensorEmulationAlg(InsAlgorithm):
    def __init__(self, imu, gps):
        super().__init__()
        self.inputs = ["time", "ref_pos", "ref_vel", "ref_att"]
        self.outputs = ["ref_gyro", "ref_accel", "gyro", "accel", "gps_ecef", "gps"]
        self.name = "INS-IMU Sensor Emulation"
        self.imu = imu
        self.gps = gps

    def __str__(self):
        return "InsAlgorithm(Sensor Emulation Algorithm)"

    def compute(self, time, ref_pos_lld, ref_vel_eb_n, ref_euler_att):
        true_gyro, true_accel = self._compute_true_imu_readouts(time, ref_pos_lld, ref_vel_eb_n, ref_euler_att)
        sampling_time = float(time[1] - time[0])

        # compute error readouts
        self._corrupt_noise_imu(true_gyro, true_accel, sampling_time)
        self._corrupt_noise_gps(ref_pos_lld, ref_vel_eb_n)

    def _corrupt_noise_imu(self, true_gyro, true_accel, sampling_time):
        for sensor, true_read in zip(["gyroscope", "accelerometer"], [true_gyro, true_accel]):
            readout = self._add_errors_imu(sensor, true_read, sampling_time)

            self.results.append(readout)

    def _add_misalignment(self, readouts, misalignment):
        for i in range(len(readouts)):
            M = rot1(misalignment[i, 0]) @ rot2(misalignment[i, 1]) @ rot3(misalignment[i, 2])
            readouts[i, :] = M @ readouts[i, :]

    def _add_errors_imu(self, sensor, true_read, sampling_time):
        user_models = self.imu[sensor]

        misalignment = user_models["misalignment"].get_stochastic_process(len(true_read)).compute(sampling_time)
        scale_factor = user_models["scale_factor"].get_stochastic_process(len(true_read)).compute(sampling_time)
        bias_constant = user_models["bias_constant"].get_stochastic_process(len(true_read)).compute(sampling_time)
        bias_drift = user_models["bias_drift"].get_stochastic_process(len(true_read)).compute(sampling_time)
        noise = user_models["observation_noise"].get_stochastic_process(len(true_read)).compute(sampling_time)

        # attach misalignment contribution
        self._add_misalignment(true_read, misalignment)

        # attach all other contributions
        readout = (1 + scale_factor) * true_read + bias_drift + bias_constant + noise

        return readout

    def _corrupt_noise_gps(self, ref_pos_lld, ref_vel_ned):
        # compute gps_pos_ecef, gps_vel_ecef (ECEF format)
        # compute gps_pos_lld, gps_vel_ned (NED format)

        # compute noise vectors
        pos_noise = self.gps.get_stochastic_process(len(ref_pos_lld), "position").compute()
        vel_noise = self.gps.get_stochastic_process(len(ref_vel_ned), "velocity").compute()

        # compute reference ecef position
        ref_pos_ecef = lld2ecef(ref_pos_lld)
        gps_pos_ecef = np.zeros(np.shape(ref_pos_ecef))

        # add noise to NED velocity
        gps_vel_ned = ref_vel_ned + vel_noise
        gps_vel_ecef = np.zeros(np.shape(gps_vel_ned))

        # epoch loop
        for i in range(len(ref_pos_lld)):
            # get rotation matrix C_e^n (ECEF to NED)
            c_e_n = matrix_ecef2ned(ref_pos_lld[i, 0], ref_pos_lld[i, 1])

            # add noise to gps ecef position
            gps_pos_ecef[i, :] = ref_pos_ecef[i, :] + c_e_n.T @ pos_noise[i, :]

            # convert ned velocity to ecef
            gps_vel_ecef[i, :] = c_e_n.T @ gps_vel_ned[i, :]

        # transform gps ecef position to LLD form
        gps_pos_lld = ecef2lld(gps_pos_ecef)

        # ecef output
        gps_ecef = np.concatenate((gps_pos_ecef, gps_vel_ecef), axis=1)
        self.results.append(gps_ecef)

        # ned output
        gps_ned = np.concatenate((gps_pos_lld, gps_vel_ned), axis=1)
        self.results.append(gps_ned)

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
