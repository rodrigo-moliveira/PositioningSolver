import numpy as np

from . import mechanization
from . import gravity
from . import attitude


class INSPropagator:
    def __init__(self, attitude_form="euler"):
        self.attitude = attitude_form
        self.w_nb_b = None

        # TODO: colocar a propagacao aqui. Do género, enviar a base de dados (gyro e accel). Depois a funcao recebe o i e o i+1 e faz as contas necessarias
        #   guardar também os resultados anteriores...

    def ins_diff_eq(self, step, lld, att, v_eb_n, w_ib_b, f_ib_b, c_bn=None):

        if c_bn is None:
            c_bn = attitude.matrix_ned2body(att).T

        # get intermediate vectors
        w_ie_n = mechanization.compute_w_ie_n(lld[0])
        w_en_n, rm_effective, rn_effective = mechanization.compute_w_en_n(v_eb_n, lld)
        r_eb_e = gravity.lld2ecef(lld)
        g_eb_e = gravity.grav_acceleration(r_eb_e)
        c_en = attitude.matrix_ecef2ned(lld[0], lld[1])  # matrix from e to n

        # compute w_nb_b
        self.w_nb_b = w_ib_b - c_bn.T @ (w_en_n + w_ie_n)

        # attitude dot
        att_dot = self._att_dot(att, step)

        # velocity dot
        vel_dot = self._vel_dot(w_en_n, w_ie_n, c_bn, f_ib_b, c_en @ g_eb_e, v_eb_n)

        # position dot
        lld_dot = self._lld_dot(lld, v_eb_n)

        return lld_dot, vel_dot, att_dot

    def _att_dot(self, att, step):
        if self.attitude == "euler":
            phi, theta, psi = att

            phi_dot = (self.w_nb_b[1] * np.sin(phi) + self.w_nb_b[2] * np.cos(phi)) * np.tan(theta) + self.w_nb_b[0]
            theta_dot = self.w_nb_b[1] * np.cos(phi) - self.w_nb_b[2] * np.sin(phi)
            psi_dot = (self.w_nb_b[1] * np.sin(phi) + self.w_nb_b[2] * np.cos(phi)) / np.cos(theta)

            return np.array([phi_dot, theta_dot, psi_dot])

        else:  # attitude == "dcm"
            sig = np.linalg.norm(self.w_nb_b)
            B = attitude.vector2skew_symmetric(self.w_nb_b)
            Sn = B / sig

            return np.eye(3) + np.sin(sig*step)*Sn + (1-np.cos(sig*step))*Sn**2

    def _vel_dot(self, w_en_n, w_ie_n, c_bn, f_ib_b, g_n, v_eb_n):

        # compute skew matrices
        skew_en_n = attitude.vector2skew_symmetric(w_en_n)
        skew_ie_n = attitude.vector2skew_symmetric(w_ie_n)

        v_eb_n_dot = c_bn @ f_ib_b + g_n - (skew_en_n + 2 * skew_ie_n) @ v_eb_n

        return v_eb_n_dot

    def _lld_dot(self, lld, v_eb_n):

        # get Earth radius
        rm, rn = gravity.get_earth_radii(lld[0])
        rm_effective = rm - lld[2]
        rn_effective = rn - lld[2]

        # get lat, lon and down dots
        lat_dot = v_eb_n[0] / rm_effective
        lon_dot = v_eb_n[1] / rn_effective / np.cos(lld[0])
        d_dot = v_eb_n[2]

        return np.array([lat_dot, lon_dot, d_dot])
