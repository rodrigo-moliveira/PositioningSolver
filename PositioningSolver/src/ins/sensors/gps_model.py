# class to store the GPS model
import json
import os
from pathlib import Path

__PATH__ = Path(__file__).parent.absolute()

import numpy as np

SENSOR_PATH_MAP = {
    "low-end": os.path.abspath(__PATH__ / "../../../inputs/sensors/low-end/gps.json"),
    "mid-end": os.path.abspath(__PATH__ / "../../../inputs/sensors/mid-end/gps.json"),
    "high-end": os.path.abspath(__PATH__ / "../../../inputs/sensors/high-end/gps.json")
}


class GPS:
    def __init__(self, accuracy):

        # initialize data dict
        self._data = {
            "position": np.array([0, 0, 0]),
            "velocity": np.array([0, 0, 0])
        }

        if isinstance(accuracy, str):

            # accuracy is 'low-end', 'mid-end' or 'high-end'
            if accuracy in SENSOR_PATH_MAP.keys():
                path = SENSOR_PATH_MAP[accuracy]

            # accuracy is the path to a gps json file
            else:
                path = accuracy

            # if path exists
            if Path(path).exists():
                with open(path) as json_file:
                    json_dict = json.load(json_file)

                    # set data
                    self.set(json_dict)
            else:
                self._raise(accuracy)
        else:
            raise self._raise(accuracy)

    def set(self, json_dict):
        self._data["position"] = np.array(json_dict["position"]["std"])
        self._data["velocity"] = np.array(json_dict["velocity"]["std"])

    def __str__(self):
        return f"IMU[{str(self._data)}]"

    def _raise(self, arg):
        raise AttributeError(f"Argument 'accuracy' {arg} is not valid. Must be a string 'low-end', 'mid-end', "
                             f" 'high-end', or, alternatively, a path to a valid gps json file")
