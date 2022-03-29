import os

from PositioningSolver.src.algorithms.ins.sensor_emul import imu_emulation
from PositioningSolver.src.ins.gravity import lla2ecef
from PositioningSolver.src.io_manager.import_timeseries.read_tm import read_csv, downsample, swap_columns
from PositioningSolver.src.math_utils.Constants import Constant

WORKSPACE = os.path.abspath("../../workspace/datasets/ins_coil_move/")


def main():
    ref_pos_file = "\\reference\\ref_pos.csv"
    ref_att_file = "\\reference\\ref_att_euler.csv"
    ref_time_file = "\\time.csv"
    ref_vel_file = "\\reference\\ref_vel.csv"

    # Read Reference PVAT
    #   Position -> LLA (lat, long, height), in [deg, deg, m]
    #   Velocity -> body velocity with respect to ECEF in navigation coordinates, v_eb_n, in [m/s]
    #   Attitude -> Euler Angles in 3-2-1 (z-y-x) rotation, that is, (phi, theta, psi) = (roll, pitch, yaw), in [deg]
    position_lla = read_csv(WORKSPACE+ref_pos_file, True, delimiter=",", factor=[Constant.DEG2RAD, Constant.DEG2RAD, 1])
    time = read_csv(WORKSPACE+ref_time_file, True, delimiter=",")
    euler = read_csv(WORKSPACE + ref_att_file, True, delimiter=",",
                     factor=[Constant.DEG2RAD, Constant.DEG2RAD, Constant.DEG2RAD],
                     function=lambda x: swap_columns(x, 0, 2))
    velocity = read_csv(WORKSPACE + ref_vel_file, True, delimiter=",")


    # transform position lla to cartesian ECEF coordinates
    # position = lla2ecef(position_lla)

    # TODO check if it makes sense to adjust frequency and apply some down sampling
    # period = time[1] - time[0]
    # frequency = 1  # output frequency, in Hz
    # position = downsample(position, period, frequency)
    # time = downsample(time, period, frequency)
    # euler = downsample(euler, period, frequency)

    imu_emulation(time, position_lla, velocity, euler)


if __name__ == "__main__":
    main()
