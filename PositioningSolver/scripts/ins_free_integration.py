import os
import numpy as np

from PositioningSolver.src.algorithms.ins.ins_integration import FreeIntegrationAlg
from PositioningSolver.src.ins.data_mng.unit_conversions import convert_unit
from PositioningSolver.src.ins.ins_alg_manager import InsAlgorithmManager
from PositioningSolver.src.io_manager.import_pvat import swap_columns


def main():
    # from ref
    WORKSPACE = os.path.abspath("C:\\Users\\rooo\\Documents\\worspace\\meus\\PositioningSolver\\workspace\\datasets\\ins_coil_move")
    gyro_file = "\\imu\\ref_gyro.csv"
    accel_file = "\\imu\\ref_accel.csv"
    time_file = "\\time.csv"
    ref_pos_file = "\\reference\\ref_pos.csv"
    ref_att_file = "\\reference\\ref_att_euler.csv"
    ref_time_file = "\\time.csv"
    ref_vel_file = "\\reference\\ref_vel.csv"

    # from output
    #WORKSPACE = os.path.abspath("../../workspace/outputs_ins/2022-05-17-15-18-42/")
    #gyro_file = "\\ref_gyro.csv"
    #accel_file = "\\ref_accel.csv"
    # time_file = "\\time.csv"

    # define initial state  TODO: note that velocity may either be given in e, n or b
    # TODO: estas coisas têm que ir para o ficheiro de config
    att0 = np.array([0, 0, 0])  # roll, pitch, yaw attitude angles
    pos0 = convert_unit(np.array([3.20e+01, 119.99999999999999, 0.]),  # lat, lon, down
                        ("deg", "deg", "m"), ("rad", "rad", "m"))
    vel0 = np.array([0, 0, 0])  # vel_ned

    # create algorithm object
    alg = FreeIntegrationAlg(pos0, vel0, att0)
    ins_mng = InsAlgorithmManager(alg)

    ins_mng.read_input_pvat(
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

    ins_mng.read_input_sensor_data(
        # Time
        {"filepath": WORKSPACE + time_file, "units": ["s"],
         "ignore_header": True, "delimiter": ",", "usecols": None, "function": None},

        # Gyroscope Measurements
        {"filepath": WORKSPACE + gyro_file, "units": ["deg/s", "deg/s", "deg/s"],
         "ignore_header": True, "delimiter": ",", "usecols": None, "function": None},

        # Accelerometer Measurements
        {"filepath": WORKSPACE + accel_file, "units": ["m/s^2", "m/s^2", "m/s^2"],
         "ignore_header": True, "delimiter": ",", "usecols": None, "function": None},
    )

    ins_mng.run()
    ins_mng.results("", performance=True)


if __name__ == "__main__":
    main()
