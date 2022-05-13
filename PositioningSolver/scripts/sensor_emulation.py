import os

from PositioningSolver.src.ins.ins_alg_manager import InsAlgorithmManager
from PositioningSolver.src.ins.sensors.gps_model import GPS
from PositioningSolver.src.ins.sensors.imu_model import IMU
from PositioningSolver.src.io_manager.import_pvat import swap_columns
from PositioningSolver.src.algorithms.ins.sensor_emul import SensorEmulationAlg


def main():
    # TODO- we will need a json configuration file with these inputs...
    WORKSPACE = os.path.abspath("../../workspace/datasets/ins_coil_move/")
    ref_pos_file = "\\reference\\ref_pos.csv"
    ref_att_file = "\\reference\\ref_att_euler.csv"
    ref_time_file = "\\time.csv"
    ref_vel_file = "\\reference\\ref_vel.csv"
    imu_str = "low-end"
    gps_str = "low-end"

    # create algorithm object
    alg = SensorEmulationAlg()

    imu = IMU(imu_str)
    gps = GPS(gps_str)

    ins_mng = InsAlgorithmManager(alg, imu, gps)

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

    ins_mng.run()

    ins_mng.results("")

    # TODO check if it makes sense to adjust frequency and apply some down sampling
    # period = time[1] - time[0]
    # frequency = 1  # output frequency, in Hz
    # position = downsample(position, period, frequency)
    # time = downsample(time, period, frequency)
    # euler = downsample(euler, period, frequency)


if __name__ == "__main__":
    main()
