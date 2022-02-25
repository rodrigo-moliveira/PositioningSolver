from PositioningSolver import scripts

from PositioningSolver.src.algorithms import __algorithms_description__
from PositioningSolver.src.common_log.logger import clean_logs


def PositioningSolver(algorithm_id, config_file):
    clean_logs()

    print(f"Running {__algorithms_description__[algorithm_id]['description']} with config file {config_file} ...")

    if algorithm_id == 0:
        # run GNSS Single Point Positioning for 1 Constellation and 1 Frequency
        scripts.gnss_spp.main(config_file)

    if algorithm_id == 1:
        # run GNSS Single Point Positioning for 1 Constellation and 1 Frequency
        scripts.gnss_plots.main(config_file)

    print("Successfully ran", __algorithms_description__[algorithm_id]["description"], "\n")
