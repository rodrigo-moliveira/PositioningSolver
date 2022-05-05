# Class to store the IMU Model (stochastic model stats)
# até posso colocar aqui a adição dos valores dos erros...

"""
Available stochastic models:
    - White Noise
    - Gauss Markov (may resort to Random Walk)
    - Random Constant
    - Constant

Definir o sensors model:
    - scale factor
        * constant or random constant or Gauss Markov
    - misalignment
        * constant or random constant or Gauss Markov
    - observation noise
        * White Noise
    - bias constant + bias stability drift
        * (Random constant or Constant) + ( Gauss Markov or Random Walk)


"""
import os

from PositioningSolver.src.io_manager.import_imu import read_imu_file

SENSOR_PATH_MAP = {
    "low-end": os.path.abspath("../../PositioningSolver/inputs/sensors/low-end/imu.json"),
    "mid-end": os.path.abspath("../../PositioningSolver/inputs/sensors/mid-end/imu.json"),
    "high-end": os.path.abspath("../../PositioningSolver/inputs/sensors/high-end/imu.json")
}


class _Process:
    def __init__(self):
        self.process = None
        self.stats = None

    def set(self, process, stats):
        self.process = process
        self.stats = stats

    def __str__(self):
        return f"Process({self.process}, stats={self.stats})"

    def __repr__(self):
        return str(self)


class IMU:

    def __init__(self, accuracy):

        # initialize data dict
        self._data = {
            "gyroscope": {
                "misalignment": _Process(),
                "scale_factor": _Process(),
                "bias_constant": _Process(),
                "bias_drift": _Process(),
                "observation_noise": _Process()
            },
            "accelerometer": {
                "misalignment": _Process(),
                "scale_factor": _Process(),
                "bias_constant": _Process(),
                "bias_drift": _Process(),
                "observation_noise": _Process()
            }
        }

        if isinstance(accuracy, str):
            if accuracy in SENSOR_PATH_MAP.keys():
                path = SENSOR_PATH_MAP[accuracy]
            else:
                path = accuracy

            # read imu file (may raise exceptions)
            read_imu_file(path, self)
        else:
            raise AttributeError(f"Provided 'accuracy' argument is not valid. Must be a string 'low-end', 'mid-end', "
                                 f" 'high-end', or, alternatively, a path to a valid imu json file")

    def set(self, sensor, model, process, stats):
        self._data[sensor][model].set(process, stats)

    def __str__(self):
        return f"IMU[{str(self._data)}]"
