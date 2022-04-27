import json

_SENSORS = ['gyroscope', 'accelerometer']
_ERROR_MODELS = ['misalignment', 'scale_factor', 'bias_constant', 'bias_drift', 'observation_noise']
_STOCHASTIC_PROCESSES = ["gauss_markov", "random_constant", "constant", "white_noise"]


def _validate_file(json_dict):
    # mandatory keys 'name', 'accelerometer' and 'gyroscope'
    pass

def _validate_misalignment():
    return True

def _validate_sf():
    return True

def _validate_bias_constant():
    return True

def _validate_bias_drift():
    return True

def _validate_obs_noise():
    return True

def read_imu_file(imu_object):
    file = "C:\\Users\\rooo\\Documents\\worspace\\meus\\PositioningSolver\\PositioningSolver\\inputs\\sensors\\imu.json"


    # Opening JSON file
    with open(file) as json_file:
        json_dict = json.load(json_file)

        # validate file

        print(json_dict["accelerometer"])


read_imu_file(None)