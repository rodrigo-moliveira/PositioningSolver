import numpy as np

from PositioningSolver.src.algorithms.ins.ins_alg import InsAlgorithm
from PositioningSolver.src.ins import mechanization
from PositioningSolver.src.ins.mechanization import get_earth_radii, dcm2euler, matrix_ned2body
from PositioningSolver.src.math_utils.matrix import vector2skew_symmetric


class FreeIntegrationAlg(InsAlgorithm):
    def __init__(self, r0, v0, att0, integration="euler"):
        super().__init__()
        self.inputs = ["time", "gyro", "accel"]
        self.outputs = ["pos", "vel", "att"]  # TODO save vel_ecef, vel_ned, vel_body ???

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

        if integration.lower() not in ["euler", "rk4"]:
            raise AttributeError(f"integration must either be 'euler' or 'rk4'")
        self.integration = integration.lower()

    def __str__(self):
        return "InsAlgorithm(Free Integration)"

    def compute(self, time, gyro, accel):
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
            accel[i - 1,:] = np.array([132, 10, 9.4])
            gyro[i - 1,:] = np.array([0.3, -3, 2])

            self.vel_eb_n[i - 1] = np.array([40,523,-2])
            self.pos[i-1] = np.array([1,3,100])
            self.att[i-1] = np.array([1,-2,0.42])

            c_bn = mechanization.matrix_ned2body(self.att[i-1]).T

            # get state at t_{i-1}
            #c_bn = self.c_bn[i-1]

            v_eb_n = self.vel_eb_n[i-1]
            lld = self.pos[i-1]
            w_ib_b = gyro[i-1]
            f_ib_b = accel[i-1]
            step = 0.01

            # get intermediate vectors at time t_{i-1}
            w_ie_n = mechanization.compute_w_ie_n(lld[0])
            w_en_n, rm_effective, rn_effective = mechanization.compute_w_en_n(v_eb_n, lld)
            r_eb_e = mechanization.lld2ecef(lld)
            g_eb_e = mechanization.grav_acceleration(r_eb_e)
            skew_en_n = vector2skew_symmetric(w_en_n)
            skew_ie_n = vector2skew_symmetric(w_ie_n)
            skew_ib_b = vector2skew_symmetric(w_ib_b)
            c_en = mechanization.matrix_ecef2ned(lld[0], lld[1])  # matrix from e to n
            w_nb_b = w_ib_b - c_bn.T @ (w_en_n + w_ie_n)
            #print("w_en_n, w_ie_n", w_en_n, w_ie_n)
            # attitude dot
            phi, theta, psi = self.att[i-1]
            phi_dot = (w_nb_b[1] * np.sin(phi) + w_nb_b[2]*np.cos(phi))*np.tan(theta)+w_nb_b[0]
            theta_dot = w_nb_b[1]*np.cos(phi)-w_nb_b[2]*np.sin(phi)
            psi_dot = (w_nb_b[1]*np.sin(phi)+w_nb_b[2]*np.cos(phi))/np.cos(theta)
            print("phi_dot, theta_dot, psi_dot", phi_dot, theta_dot, psi_dot)

            #print("rm, rn, g", rm_effective, rn_effective, c_en@g_eb_e)
            #print("w_nb_b", w_ib_b - c_bn.T@(w_en_n + w_ie_n))
            # compute derivatives at time t_{i-1}
            c_bn_dot = c_bn @ skew_ib_b - (skew_ie_n + skew_en_n) @ c_bn


            v_eb_n_dot = c_bn @ f_ib_b + c_en @ g_eb_e - (skew_en_n + 2 * skew_ie_n) @ v_eb_n
            #g=c_en @ g_eb_e
            #g[0]=0;g[1]=0
            #v_eb_n_dot = c_bn @ f_ib_b + g - (skew_en_n + 2 * skew_ie_n) @ v_eb_n
            #print("terms", c_bn @ f_ib_b, g, (skew_en_n + 2 * skew_ie_n) @ v_eb_n)


            # ! temp !
            rm, rn = get_earth_radii(lld[0])
            rm_effective = rm - lld[2]
            rn_effective = rn - lld[2]
            lat_dot = v_eb_n[0] / rm_effective
            lon_dot = v_eb_n[1] / rn_effective / np.cos(lld[0])
            d_dot = v_eb_n[2]
            #print("pos_dot, vel_dot", np.array([lat_dot, lon_dot, d_dot]), v_eb_n_dot)

            # apply euler integration step from t_{i-1} to t_{i} and save results at index i
            pos_i = lld + np.array([lat_dot, lon_dot, d_dot]) * step
            vel_i = v_eb_n + v_eb_n_dot * step
            #c_bn_i = c_bn + c_bn_dot * step

            #print(c_bn_dot)
            #att = dcm2euler(c_bn_i)
            att2 = self.att[i-1] + np.array([phi_dot, theta_dot, psi_dot])*step
            c_bn_2 = mechanization.matrix_ned2body(att2).T

            #print("attitudes!", att, att2)
            #print("final pos, vel, att", pos_i, vel_i, att)
            #print("final c_bn", c_bn_i)

            # save results
            self.c_bn.append(c_bn_2)
            #print(self.c_bn)
            self.vel_eb_n[i] = vel_i
            self.pos[i] = pos_i
            #exit()
            print(pos_i, vel_i, att2)
            exit()

        #print(len(self.pos));exit()
        self.results.append(self.pos)
        self.results.append(self.vel_eb_n)
        self.results.append(self.att)
