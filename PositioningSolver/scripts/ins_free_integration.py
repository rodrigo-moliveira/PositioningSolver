import os
import numpy as np

from PositioningSolver.src.algorithms.ins.ins_integration import FreeIntegrationAlg
from PositioningSolver.src.ins.data_mng.unit_conversions import convert_unit
from PositioningSolver.src.ins.ins_alg_manager import InsAlgorithmManager


def main():
    # from ref
    WORKSPACE = os.path.abspath("C:\\Users\\rooo\\Documents\\worspace\\meus\\gnss-ins-sim\\demo_saved_data\\2022-05-20-20-19-57")
    gyro_file = "\\ref_gyro.csv"
    accel_file = "\\ref_accel.csv"
    time_file = "\\time.csv"

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
    ins_mng.results("")


if __name__ == "__main__":
    main()
