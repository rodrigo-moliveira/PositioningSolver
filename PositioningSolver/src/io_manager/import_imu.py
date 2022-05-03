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

def read_imu_file(path, imu):

    # Opening JSON file
    with open(path) as json_file:
        json_dict = json.load(json_file)

        # TODO add file validation

        process = json_dict["accelerometer"]["misalignment"]["select_model"]
        # TODO fazer funcao que recebe o processo e sabe quais sao os parametros a elr e retorna os stats...
        stats = None
        imu.set("accelerometer", process, None)
