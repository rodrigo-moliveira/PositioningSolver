import glob

from ...data_types.basics.Epoch import Epoch
from ...io_manager.import_rinex.RinexNavReaderGPS import RinexNavReaderGPS
from ...io_manager.import_rinex.RinexObsReader import RinexObsReader

from ... import get_logger


def read_data(services, obs_data, obs_header, nav_data, path_to_obs, path_to_nav,
              first_epoch, last_epoch, snr_control, trace_file_path):
    log = get_logger("io_manager")
    log.info("#########################################################")
    log.info("###### Starting module 'Read Input Data Files' ... ######")

    _first_epoch = _last_epoch = None
    try:
        if isinstance(first_epoch, str):
            _first_epoch = Epoch(first_epoch)
            log.info(f"Initial epoch: {_first_epoch.to_time_stamp()}")
    except:
        log.warning(f"Failed to parse initial epoch from input string {first_epoch}")

    try:
        if isinstance(last_epoch, str):
            _last_epoch = Epoch(last_epoch)
            log.info(f"Final epoch: {_last_epoch.to_time_stamp()}")
    except:
        log.warning(f"Failed to parse final epoch from input string {last_epoch}")
    
    # read navigation files
    files = glob.glob(path_to_nav + "/*")
    if len(files) == 0: raise AttributeError(f"No valid navigation file provided. Please check file paths")
    for file in files:
        log.info("Reading file {}...".format(file))
        try:
            RinexNavReaderGPS(file, nav_data)
            # RinexNavReaderGAL(...)

        except Exception as e:
            log.warning(f"Failed to read file {file} as a navigation file")

    # read observation files
    files = glob.glob(path_to_obs + "/*")
    if len(files) == 0: raise AttributeError(f"No valid observation file provided. Please check file paths")
    for file in files:
        log.info("Reading file {}...".format(file))
        try:
            RinexObsReader(file, services, obs_data, obs_header, log, _first_epoch, _last_epoch, snr_control)

        except Exception as e:
            log.warning(f"Failed to read file {file} as an observation file file")

    # write to trace file
    log.debug("Writing Navigation Data to trace file {}".format("NavigationData.txt"))
    f = open(trace_file_path + "/NavigationData.txt", "w")
    f.write(str(nav_data))
    f.close()

    log.debug("Writing Observation Data to trace file {}".format("RawObservationData.txt"))
    f = open(trace_file_path + "/ObservationData.txt", "w")
    f.write(str(obs_header) + "\n" + str(obs_data))
    f.close()

    log.info(f"Available Satellites: {obs_data.get_satellite_list()}")
    log.info("####### End of module 'Read Input Data Files' ... #######\n")

