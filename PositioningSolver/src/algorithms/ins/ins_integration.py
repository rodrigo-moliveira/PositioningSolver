import numpy as np
from scipy.linalg import sqrtm, inv

from PositioningSolver.src.algorithms.ins.ins_alg import InsAlgorithm
from PositioningSolver.src.ins import mechanization
from PositioningSolver.src.ins.mechanization import dcm2euler, fix_angles
from PositioningSolver.src.ins.mechanization.propagation import INSPropagator


class FreeIntegrationAlg(InsAlgorithm):
    def __init__(self, r0, v0, att0, integration="euler", attitude_form="euler"):
        super().__init__()
        self.name = "INS-IMU Free Integration"
        self.inputs = ["time", "gyro", "accel"]
        self.outputs = ["pos", "vel", "att"]  # TODO save vel_ecef, vel_ned, vel_body ???
        # TODO: save pos_ecef...
        # store initial condition
        self.r0 = r0  # initial position in lld form
        self.v0 = v0  # initial velocity in ned, v_eb_n
        self.att0 = att0  # initial attitude in (roll, pitch, yaw)

        # Integration outputs
        self.att = None
        self.pos = None
        self.vel_eb_n = None
        self.vel_eb_b = None
        self.c_bn = None

        # Integrator object
        if integration.lower() not in ["euler", "rk4"]:
            raise AttributeError(f"integration must either be 'euler' or 'rk4'")
        self.integration = integration.lower()

        # propagator object
        if attitude_form.lower() not in ["euler", "dcm"]:
            raise AttributeError(f"attitude_form must either be 'euler' or 'dcm'")
        self.attitude_form = attitude_form
        self.prop = INSPropagator(attitude_form=attitude_form)  # euler or dcm

    def __str__(self):
        return "InsAlgorithm(Free Integration)"

    def compute(self, time, gyro, accel):
        if self.integration == "euler":
            self.compute_euler(time, gyro, accel)
        else:
            self.compute_rk4(time, gyro, accel)

    def compute_euler(self, time, gyro, accel):
        if len(time) != len(gyro) or len(time) != len(accel) or len(gyro) != len(accel):
            raise ValueError(f"Provided vectors must have the same time-length. Time has length {len(time)}"
                             f", gyro length {len(gyro)} and accel length {len(accel)}")

        # create output vectors
        n = len(accel)
        self.att = np.zeros((n, 3))
        self.pos = np.zeros((n, 3))
        self.vel_eb_n = np.zeros((n, 3))  # NED vel
        self.vel_eb_b = np.zeros((n, 3))  # body vel
        self.c_bn = []

        # initialize with initial condition at t0
        self.att[0] = self.att0
        self.pos[0] = self.r0
        self.vel_eb_n[0] = self.v0
        c_nb0 = mechanization.matrix_ned2body(self.att0)
        self.vel_eb_b = c_nb0 @ self.v0
        self.c_bn.append(c_nb0.T)

        for i in range(1, len(time)):

            # get state at t_{i-1}
            att = self.att[i-1]
            c_bn = self.c_bn[i-1]
            v_eb_n = self.vel_eb_n[i-1]
            lld = self.pos[i-1]
            w_ib_b = gyro[i-1]
            f_ib_b = accel[i-1]
            step = time[i] - time[i-1]

            # implement x_dot = f(x,u)
            lld_dot, vel_dot, att_dot = self.prop.ins_diff_eq(step, lld, att, v_eb_n, w_ib_b, f_ib_b, c_bn=c_bn)

            # euler integration step from t_{i-1} to t_{i} and save results at index i
            pos_i = lld + lld_dot * step
            vel_i = v_eb_n + vel_dot * step

            # attitude update depends on state form (may be euler angles or dcm matrix)
            if self.attitude_form == "euler":
                att_i = att + att_dot * step
                fix_angles(att_i)
                c_bn_i = mechanization.matrix_ned2body(att_i).T

            else:  # self.attitude_form == "dcm"
                c_bn_i = c_bn @ att_dot
                # https://www.quora.com/How-can-I-quickly-compute-the-nearest-orthogonal-matrix-or-rotation-matrix-to-a-given-3x3-matrix
                c_bn_i = c_bn_i @ inv(sqrtm(c_bn_i.T @ c_bn_i))
                c_bn_i = np.real(c_bn_i)

                att_i = dcm2euler(c_bn_i)
                fix_angles(att_i)

            # save results for this iteration
            self.c_bn.append(c_bn_i)
            self.vel_eb_n[i] = vel_i.copy()
            self.pos[i] = pos_i.copy()
            self.att[i] = att_i.copy()

        self.results.append(self.pos)
        self.results.append(self.vel_eb_n)
        self.results.append(self.att)
        # TODO: convert lld to ecef and save.

    def compute_rk4(self, time, gyro, accel):
        if len(time) != len(gyro) or len(time) != len(accel) or len(gyro) != len(accel):
            raise ValueError(f"Provided vectors must have the same time-length. Time has length {len(time)}"
                             f", gyro length {len(gyro)} and accel length {len(accel)}")

        # create output vectors
        n = len(accel)
        self.att = np.zeros((n, 3))
        self.pos = np.zeros((n, 3))
        self.vel_eb_n = np.zeros((n, 3))  # NED vel
        self.vel_eb_b = np.zeros((n, 3))  # body vel
        self.c_bn = []

        # initialize with initial condition at t0
        self.att[0] = self.att0
        self.pos[0] = self.r0
        self.vel_eb_n[0] = self.v0
        c_nb0 = mechanization.matrix_ned2body(self.att0)
        self.vel_eb_b = c_nb0 @ self.v0
        self.c_bn.append(c_nb0.T)

        step = time[2] - time[0]  # step de integracao

        for i in range(0, len(time)-2, 2):

            # get state at t_i
            att = self.att[i].copy()
            v_eb_n = self.vel_eb_n[i].copy()
            lld = self.pos[i].copy()
            w_ib_b = gyro[i].copy()
            f_ib_b = accel[i].copy()

            # K1
            K1_lld_dot, K1_vel_dot, K1_att_dot = self.prop.ins_diff_eq(step, lld, att, v_eb_n, w_ib_b, f_ib_b)

            # K2
            att_2 = att + step/2 * K1_att_dot
            fix_angles(att_2)
            v_eb_n_2 = v_eb_n + step / 2 * K1_vel_dot
            lld_2 = lld + step / 2 * K1_lld_dot
            w_ib_b = gyro[i+1].copy()
            f_ib_b = accel[i+1].copy()
            K2_lld_dot, K2_vel_dot, K2_att_dot = self.prop.ins_diff_eq(step, lld_2, att_2, v_eb_n_2, w_ib_b, f_ib_b)

            # K3
            att_3 = att + step / 2 * K2_att_dot
            fix_angles(att_3)
            v_eb_n_3 = v_eb_n + step / 2 * K2_vel_dot
            lld_3 = lld + step / 2 * K2_lld_dot
            K3_lld_dot, K3_vel_dot, K3_att_dot = self.prop.ins_diff_eq(step, lld_3, att_3, v_eb_n_3, w_ib_b, f_ib_b)

            # K4
            att_4 = att + step * K3_att_dot
            fix_angles(att_4)
            v_eb_n_4 = v_eb_n + step * K3_vel_dot
            lld_4 = lld + step * K3_lld_dot
            w_ib_b = gyro[i+2].copy()
            f_ib_b = accel[i+2].copy()
            K4_lld_dot, K4_vel_dot, K4_att_dot = self.prop.ins_diff_eq(step, lld_4, att_4, v_eb_n_4, w_ib_b, f_ib_b)

            # compute
            att_f = att + step / 6 * (K1_att_dot + (2 * K2_att_dot) + (2 * K3_att_dot) + K4_att_dot)
            fix_angles(att_f)
            vel_f = v_eb_n + step / 6 * (K1_vel_dot + 2 * K2_vel_dot + 2 * K3_vel_dot + K4_vel_dot)
            lld_f = lld + step / 6 * (K1_lld_dot + 2 * K2_lld_dot + 2 * K3_lld_dot + K4_lld_dot)

            # save
            self.vel_eb_n[i+2] = vel_f.copy()
            self.pos[i+2] = lld_f.copy()
            self.att[i+2] = att_f.copy()
            self.vel_eb_n[i + 1] = None
            self.pos[i + 1] = None
            self.att[i + 1] = None

        self.vel_eb_n[len(time)-1] = None
        self.pos[len(time)-1] = None
        self.att[len(time)-1] = None

        self.results.append(self.pos)
        self.results.append(self.vel_eb_n)
        self.results.append(self.att)
