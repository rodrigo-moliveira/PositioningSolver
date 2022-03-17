import os

from PositioningSolver.src import set_logs
from PositioningSolver.src.common_log import get_logger
from ..src.algorithms.gnss.gnss_solver.gps_solver import GPSSolver
from ..src.algorithms.gnss.preprocessor.preprocessor_manager import Preprocessor
from ..src.config import config, validate_config

from PositioningSolver.src.gnss.data_types.DataManager import GNSSDataManager
from PositioningSolver.src.gnss.data_types import SatelliteSystem
from PositioningSolver.src.gnss.state_space.gnss_state import PositionGNSS
from ..src.io_manager.import_rinex import read_data
from ..src.quality_check.qm_gnss import GNSSQualityManager
from ..src.utils.errors import ConfigError

__code__ = "gnss_spp"


def setup(path_to_config_file):
    # read user configurations
    config.read_configure_json(path_to_config_file)
    try:
        validate_config(__code__)  # TODO add validation function
    except ConfigError as e:
        raise e

    # create output folder if it does not exist yet
    output_path = config["outputs"]["output_path"] + "/output/"
    bExists = os.path.exists(output_path)
    if not bExists:
        # Create the new directory because it does not exist
        os.makedirs(output_path)

    # create trace folder if it does not exist yet
    trace_path = output_path + "trace/"

    bExists = os.path.exists(trace_path)
    if not bExists:
        # Create the new directory because it does not exist
        os.makedirs(trace_path)

    # set up loggers
    set_logs(config, output_path)

    # create and clean log file
    open(output_path + "/log.txt", 'w').close()

    return output_path, trace_path


def validate_services(service_manager):
    # Currently, only GPS L1 / L2 data is allowed
    if len(service_manager.getServicesForGAL()) > 0:
        raise ConfigError(f"In the current software version, only GPS L1 and/or L2 data is allowed."
                          f"\nPlease change Galileo to GPS")

    gps_service = service_manager.getServicesForGPS()
    for freq in gps_service:
        if int(freq[0]) != 1 and int(freq[0]) != 2:
            raise ConfigError(f"In the current software version, only GPS L1 and/or L2 data is allowed."
                              f"\nPlease change Frequency L{int(freq[0])} to the allowed ones")


def main(path_to_config_file):
    # construct data container object
    data_manager = GNSSDataManager()

    # initial setup (read config json file and create output directories)
    output_path, trace_path = setup(path_to_config_file)
    main_log = get_logger("main")
    main_log.info(f"Successfully read config file {path_to_config_file}")

    # set constellation and services
    constellation = SatelliteSystem(config["model"]["constellation"])
    observations = config["model"]["observations"]
    data_manager.set_constellation(constellation, observations)

    try:
        # 1 - Read Input Data
        read_data(data_manager.services,
                  data_manager.raw_obs_data,
                  data_manager.obs_header,
                  data_manager.nav_data,
                  config["inputs"]["rinex_obs_dir_path"],
                  config["inputs"]["rinex_nav_dir_path"],
                  config["inputs"]["arc"]["fist_epoch"],
                  config["inputs"]["arc"]["last_epoch"],
                  config["inputs"]["snr_control"]["select"],
                  trace_path)
    except Exception as e:
        main_log.exception(f"Exception in Read Input Data:\n{e}")
        exit(-1)

    # Validate services
    try:
        main_log.info(f"User-defined frequencies are {data_manager.services}")
        validate_services(data_manager.services)
    except Exception as e:
        main_log.exception(f"Exception in selected frequencies / constellations:\n{e}")
        exit(-1)

    # 2 - Process Observation Data (Get Iono Free / Smooth / Smooth Iono Free data)
    try:
        compute_iono_free = config["model"]["ionosphere"]["select"] == 2
        output_rate = config["model"]["rate"]["select"]
        preprocessor = Preprocessor(trace_path,
                                    data_manager.services,
                                    constellation,
                                    data_manager.raw_obs_data,
                                    compute_iono_free,
                                    output_rate)
        data_manager.processed_obs_data = preprocessor.compute()
    except Exception as e:
        main_log.exception(f"Exception occurred during Process Observation Data Module:\n{e}")
        exit(-1)

    # fetching proper observation data (processed or raw)
    if data_manager.processed_obs_data is None:
        observation_data = data_manager.raw_obs_data
    else:
        observation_data = data_manager.processed_obs_data

    # 3 - GNSS PVT solver module
    try:
        solver = GPSSolver(observation_data, data_manager.nav_data, config)
        solver.solve(data_manager.receiver_position, data_manager.receiver_clock,
                     data_manager.prefit_residuals, data_manager.estimated_iono,
                     data_manager.postfit_residuals, data_manager.DOPs, data_manager.sat_info)
    except Exception as e:
        main_log.exception(f"Exception occurred during GNSS PVT Solver Module:\n{e}")
        exit(-1)

    # 4 - Quality Check module
    true_position = PositionGNSS([config["performance_evaluation"]["true_position"]["x_ecef"],
                                  config["performance_evaluation"]["true_position"]["y_ecef"],
                                  config["performance_evaluation"]["true_position"]["z_ecef"]],
                                 "ECEF", "cartesian")
    try:
        GNSSQualityManager.process(output_path, trace_path, true_position,
                                   data_manager.receiver_position, data_manager.receiver_clock,
                                   data_manager.prefit_residuals, data_manager.postfit_residuals,
                                   data_manager.DOPs, data_manager.sat_info, data_manager.estimated_iono,
                                   config["outputs"]["show_plots"])
    except Exception as e:
        main_log.exception(f"Exception occurred during Quality Check Module:\n{e}")
        exit(-1)

    main_log.info("Successfully ran this scenario!")


if __name__ == "__main__":
    # example
    main("0 ./workspace/spp_1c/config.json")
