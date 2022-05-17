import os

from PositioningSolver.src.algorithms.ins.ins_integration import FreeIntegrationAlg
from PositioningSolver.src.ins.ins_alg_manager import InsAlgorithmManager


def main():
    WORKSPACE = os.path.abspath("../../workspace/datasets/ins_coil_move/")
    gyro_file = "\\imu\\gyro-0.csv"
    accel_file = "\\imu\\accel-0.csv"
    time_file = "\\time.csv"

    # define initial state


    # create algorithm object
    alg = FreeIntegrationAlg(None, None)
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
