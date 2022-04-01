import os

from PositioningSolver.src.algorithms.ins.sensor_emul import imu_emulation
from PositioningSolver.src.gnss.state_space.utils import Cartesian2Geodetic
from PositioningSolver.src.ins.attitude import matrix_ecef2ned
from PositioningSolver.src.ins.gravity import lla2ecef
from PositioningSolver.src.io_manager.import_timeseries.read_tm import read_csv, swap_columns
from PositioningSolver.src.math_utils.Constants import Constant


def main():
    WORKSPACE = os.path.abspath("../../workspace/datasets/ins_coil_move/")
    ref_pos_file = "\\reference\\ref_pos.csv"
    ref_att_file = "\\reference\\ref_att_euler.csv"
    ref_time_file = "\\time.csv"
    ref_vel_file = "\\reference\\ref_vel.csv"

    # Read Reference PVAT
    #   Position -> LLA (lat, long, height), in [deg, deg, m]
    #   Velocity -> body velocity with respect to ECEF in navigation coordinates, v_eb_n, in [m/s]
    #   Attitude -> Euler Angles in 3-2-1 (z-y-x) rotation, that is, (phi, theta, psi) = (roll, pitch, yaw), in [deg]
    # NOTE: my position is positive towards down!!! I do not apply the - correction
    # remember that altitude is positive downwards!
    # in the reference euler, the order is yaw, pitch, roll, but I use roll, pitch, yaw. Swap columns 0 with 2..
    position_lla = read_csv(WORKSPACE+ref_pos_file, True, delimiter=",", factor=[Constant.DEG2RAD, Constant.DEG2RAD, -1])
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

    # TODO: fazer uma funçao de input, que leia todos os inputs (PVAT) para um datamanager. O utilizador escolhe a
    #   forma dos inputs (e.g.: LLA or ECEF, or vel_n, or vel_e)
    #   e converte tudo para a forma standard..

    imu_emulation(time, position_lla, velocity, euler)

def main2():
    WORKSPACE = os.path.abspath("../../workspace/datasets/ins_double_loop/")
    ref_file = "\\imuEmulatorTestTrj01.csv"

    # Read Reference PVAT
    #   Position -> LLA (lat, long, height), in [deg, deg, m]
    #   Velocity -> body velocity with respect to ECEF in navigation coordinates, v_eb_n, in [m/s]
    #   Attitude -> Euler Angles in 3-2-1 (z-y-x) rotation, that is, (phi, theta, psi) = (roll, pitch, yaw), in [deg]
    position = read_csv(WORKSPACE+ref_file, ignore_header=False, delimiter=",", usecols=(1,2,3))

    time = read_csv(WORKSPACE+ref_file, ignore_header=False, delimiter=",", usecols=0, factor=1E-3)
    velocity = read_csv(WORKSPACE + ref_file, ignore_header=False, delimiter=",", usecols=(4, 5, 6))


    euler = read_csv(WORKSPACE+ref_file, False, delimiter=",",usecols=(16,17,18),
                     function=lambda x: swap_columns(x, 0, 2))


    velocity_n = velocity.copy()

    # convert velocity from v_eb_e to v_eb_n  (simply multiply by C)
    for i in range(len(time)):
        position[i] = Cartesian2Geodetic(*position[i])
        position[i,2] = -position[i,2]
        c_en = matrix_ecef2ned(position[i][0], position[i][1])
        velocity_n[i] = c_en @ velocity[i]



    # transform position lla to cartesian ECEF coordinates
    # position = lla2ecef(position_lla)

    # TODO check if it makes sense to adjust frequency and apply some down sampling
    # period = time[1] - time[0]
    # frequency = 1  # output frequency, in Hz
    # position = downsample(position, period, frequency)
    # time = downsample(time, period, frequency)
    # euler = downsample(euler, period, frequency)

    imu_emulation(time, position, velocity_n, euler)


if __name__ == "__main__":
    main()
