# set the logger
from .common_log.logger import get_logger, clean_logs


def set_logs(config, output_path):
    clean_logs()

    get_logger("main", file_level=config.get("log", "minimum_level", fallback="INFO"),
               file_path=output_path + "/log.txt")

    get_logger("io_manager", file_level=config.get("log", "minimum_level", fallback="INFO"),
               file_path=output_path + "/log.txt")

    get_logger("preprocessor", file_level=config.get("log", "minimum_level", fallback="INFO"),
               file_path=output_path + "/log.txt")

    get_logger("gps_solver", file_level=config.get("log", "minimum_level", fallback="INFO"),
               file_path=output_path + "/log.txt")

    get_logger("quality_check", file_level=config.get("log", "minimum_level", fallback="INFO"),
               file_path=output_path + "/log.txt")
