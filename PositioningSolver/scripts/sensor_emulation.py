import os

from PositioningSolver.src.gnss.state_space.utils import Cartesian2Geodetic
from PositioningSolver.src.ins.ins_alg_manager import InsAlgorithmManager
from PositioningSolver.src.ins.mechanization.attitude import matrix_ecef2ned
from PositioningSolver.src.io_manager.import_pvat import read_csv, swap_columns


def main():
    WORKSPACE = os.path.abspath("../../workspace/datasets/ins_coil_move/")
    ref_pos_file = "\\reference\\ref_pos.csv"
    ref_att_file = "\\reference\\ref_att_euler.csv"
    ref_time_file = "\\time.csv"
    ref_vel_file = "\\reference\\ref_vel.csv"

    ins_mng = InsAlgorithmManager()

    ins_mng.read_input_data(
        # Time
        {"filepath": WORKSPACE + ref_time_file, "units": ["s"],
         "ignore_header": True, "delimiter": ",", "usecols": None, "function": None},

        # Position
        {"filepath": WORKSPACE + ref_pos_file, "form": "LLA", "units": ["deg", "deg", "m"],
         "ignore_header": True, "delimiter": ",", "usecols": None, "function": None},

        # Velocity
        {"filepath": WORKSPACE + ref_vel_file, "frame": "n", "units": ["m/s", "m/s", "m/s"],
         "ignore_header": True, "delimiter": ",", "usecols": None, "function": None},

        # Attitude
        {"filepath": WORKSPACE + ref_att_file, "units": ["deg", "deg", "deg"],
         "ignore_header": True, "delimiter": ",", "usecols": None,
         "function": lambda x: swap_columns(x, 0, 2)})  # in ref file, we have (yaw, pitch, roll), but here we store
    #                                                       (roll, pitch, yaw)

    # ins.apply_algorithm()

    ins_mng.results("")

    # TODO check if it makes sense to adjust frequency and apply some down sampling
    # period = time[1] - time[0]
    # frequency = 1  # output frequency, in Hz
    # position = downsample(position, period, frequency)
    # time = downsample(time, period, frequency)
    # euler = downsample(euler, period, frequency)


    # g,a = imu_emulation(time, position_lla, velocity, euler)
    # add g e a para o INSMANAGER.. (criar uma data_SIM
    # print(a)


def main2():
    WORKSPACE = os.path.abspath("../../workspace/datasets/ins_double_loop/")
    ref_file = "\\imuEmulatorTestTrj01.csv"

    # Read Reference PVAT
    #   Position -> LLA (lat, long, height), in [deg, deg, m]
    #   Velocity -> body velocity with respect to ECEF in navigation coordinates, v_eb_n, in [m/s]
    #   Attitude -> Euler Angles in 3-2-1 (z-y-x) rotation, that is, (phi, theta, psi) = (roll, pitch, yaw), in [deg]
    position = read_csv(WORKSPACE + ref_file, ignore_header=False, delimiter=",", usecols=(1, 2, 3))

    time = read_csv(WORKSPACE + ref_file, ignore_header=False, delimiter=",", usecols=0, factor=1E-3)
    velocity = read_csv(WORKSPACE + ref_file, ignore_header=False, delimiter=",", usecols=(4, 5, 6))

    euler = read_csv(WORKSPACE + ref_file, False, delimiter=",", usecols=(16, 17, 18),
                     function=lambda x: swap_columns(x, 0, 2))

    velocity_n = velocity.copy()

    # convert velocity from v_eb_e to v_eb_n  (simply multiply by C)
    for i in range(len(time)):
        position[i] = Cartesian2Geodetic(*position[i])
        position[i, 2] = -position[i, 2]
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
