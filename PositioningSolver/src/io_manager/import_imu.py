import json
import numpy as np

from PositioningSolver.src.ins.data_mng.unit_conversions import convert_unit

_SENSORS = ['gyroscope', 'accelerometer']
_ERROR_MODELS = ['misalignment', 'scale_factor', 'bias_constant', 'bias_drift', 'observation_noise']
_STOCHASTIC_PROCESSES = ["gauss_markov", "random_constant", "constant", "white_noise"]
_UNIT_MAP = {
    "gyroscope": {
        "misalignment": ("deg", "rad"),
        "scale_factor": ("ppm", ""),
        "bias_constant": ("deg/hr", "rad/s"),
        "bias_drift": ("deg/hr", "rad/s"),
        "observation_noise": ("deg/sqrt(hr)", "rad/sqrt(s)")
    },
    "accelerometer": {
        "misalignment": ("deg", "rad"),
        "scale_factor": ("ppm", ""),
        "bias_constant": ("mg", "m/s^2"),
        "bias_drift": ("mg", "m/s^2"),
        "observation_noise": ("m/s/sqrt(hr)", "m/s/sqrt(s)")
    },
}

_PROCESS_STATS_MAP = {
    "gauss_markov": "prn",
    "random_constant": "std",
    "constant": "bias",
    "white_noise": "std"
}


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


def _get_process_stats(process, process_dict):
    stats = {}
    if process == "gauss_markov":
        stats["prn"] = process_dict["Prn"]
        stats["tau"] = process_dict["Tau"]

    elif process == "random_constant" or process == "white_noise":
        stats["std"] = process_dict["std"]

    elif process == "constant":
        stats["bias"] = process_dict["val"]

    return stats


def _convert_to_SI_units(sensor, model, process, stats):
    # get units
    unit_in, unit_out = _UNIT_MAP[sensor][model]

    vec = np.array(stats[_PROCESS_STATS_MAP[process]])
    vec_out = convert_unit(vec, 3 * [unit_in], 3 * [unit_out])

    # update stats dict
    stats[_PROCESS_STATS_MAP[process]] = vec_out


def read_imu_file(path, imu):
    # Opening JSON file
    with open(path) as json_file:
        json_dict = json.load(json_file)

        # TODO add file validation

        for sensor in _SENSORS:
            for model in _ERROR_MODELS:

                # get selected model
                if model == "bias_drift":
                    process = "gauss_markov"
                elif model == "observation_noise":
                    process = "white_noise"
                else:
                    process = json_dict[sensor][model]["select_model"]

                # print(f"processing sensor {sensor} for model {model} with process {process}")

                # get statistics for this model and process
                stats = _get_process_stats(process, json_dict[sensor][model][process])

                # convert data to SI units (degrees to rads, ref acceleration g to m/s^2)
                _convert_to_SI_units(sensor, model, process, stats)

                # set the imu for this model
                imu.set(sensor, model, process, stats)
