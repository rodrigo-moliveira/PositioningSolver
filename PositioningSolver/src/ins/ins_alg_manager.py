import os
import time

from PositioningSolver.src.ins.data_mng.ins_data_mng import InsDataManager
from PositioningSolver import OUTPUT_INS_DIR

# Internally we store:
#   position as LLD (lat long down)
#   velocity as v_eb_n (v_East, v_North, v_Down)
#   attitude as Euler angles using zyx convention (but stored in x,y,z <-> roll, pitch, yaw)
from PositioningSolver.src.ins.data_mng.unit_conversions import convert_unit
from PositioningSolver.src.ins.mechanization.dynamics import velE2velN, velB2velN
from PositioningSolver.src.ins.mechanization.gravity import lla2lld, ecef2lld
from PositioningSolver.src.io_manager.import_pvat import read_csv
from PositioningSolver.src.quality_check.qm_ins import INSQualityManager


class InsAlgorithmManager:

    def __init__(self, algorithm):
        self.data_manager = InsDataManager()
        self.algorithm = algorithm

    def read_input_pvat(self, time_dict, position_dict, velocity_dict, attitude_dict):

        # TODO: check mandatory fields
        #   Position - filepath, form, units

        # check for mandatory keys
        for key in ["filepath", "form", "units"]:
            if key not in position_dict:
                raise AttributeError(f"position_dict must have mandatory key {key}")

        # read position
        position = read_csv(position_dict.get("filepath"),
                            position_dict.get("ignore_header", True),
                            position_dict.get("delimiter", ","),
                            position_dict.get("usecols", None),
                            position_dict.get("factor", None),
                            position_dict.get("function", None))

        # transform LLA or ECEF forms to LLD
        pos_form = position_dict.get("form")
        if pos_form.upper() not in ["LLA", "LLD", "ECEF"]:
            raise AttributeError(f"position_dict must have valid 'form'. Possible values are 'LLA', 'LLD' or 'ECEF'")
        if pos_form.upper() == "LLA":
            position = convert_unit(position, position_dict.get("units"), ("rad", "rad", "m"))
            position = lla2lld(position)
        elif pos_form.upper() == "ECEF":
            # TODO: validate this!
            position = convert_unit(position, position_dict.get("units"), ("m", "m", "m"))
            position = ecef2lld(position)
        else:  # position is already in LLD form
            position = convert_unit(position, position_dict.get("units"), ("rad", "rad", "m"))
        self.data_manager.add_data("ref_pos", position, ("rad", "rad", "m"))

        # read time
        time_arr = read_csv(time_dict.get("filepath"),
                            time_dict.get("ignore_header", True),
                            time_dict.get("delimiter", ","),
                            time_dict.get("usecols", None),
                            time_dict.get("factor", None),
                            time_dict.get("function", None))
        # transform to column vector
        time_arr = time_arr.reshape(-1, 1)
        self.data_manager.add_data("time", time_arr, units=time_dict.get("units"))

        # read attitude
        attitude = read_csv(attitude_dict.get("filepath"),
                            attitude_dict.get("ignore_header", True),
                            attitude_dict.get("delimiter", ","),
                            attitude_dict.get("usecols", None),
                            attitude_dict.get("factor", None),
                            attitude_dict.get("function", None))
        self.data_manager.add_data("ref_att", attitude, attitude_dict.get("units"))

        # read velocity
        velocity = read_csv(velocity_dict.get("filepath"),
                            velocity_dict.get("ignore_header", True),
                            velocity_dict.get("delimiter", ","),
                            velocity_dict.get("usecols", None),
                            velocity_dict.get("factor", None),
                            velocity_dict.get("function", None))

        # transform velocity to navigation frame (NED components), that is, v_eb_n
        frame = velocity_dict.get("frame")
        if frame.lower() not in ["e", "n", "b"]:
            raise AttributeError(f"velocity_dict must have valid 'frame'. Possible values are 'e', 'n' or 'b'")
        if frame.lower() == "e":
            # TODO validate this
            velocity = convert_unit(velocity, velocity_dict.get("units"), ("m/s", "m/s", "m/s"))
            velocity = velE2velN(velocity, self.data_manager.get_data("ref_pos"))
        elif frame.lower() == "b":
            # TODO validate this
            velocity = convert_unit(velocity, velocity_dict.get("units"), ("m/s", "m/s", "m/s"))
            velocity = velB2velN(velocity, self.data_manager.get_data("ref_att"))
        else:  # velocity is already in n components
            velocity = convert_unit(velocity, velocity_dict.get("units"), ("m/s", "m/s", "m/s"))
        self.data_manager.add_data("ref_vel", velocity, ("m/s", "m/s", "m/s"))

    def read_input_sensor_data(self, time_dict, gyro_dict, accel_dict):
        # read time
        time_arr = read_csv(time_dict.get("filepath"),
                            time_dict.get("ignore_header", True),
                            time_dict.get("delimiter", ","),
                            time_dict.get("usecols", None),
                            time_dict.get("factor", None),
                            time_dict.get("function", None))
        # transform to column vector
        time_arr = time_arr.reshape(-1, 1)
        self.data_manager.add_data("time", time_arr, units=time_dict.get("units"))

        # read gyroscope
        gyroscope = read_csv(gyro_dict.get("filepath"),
                             gyro_dict.get("ignore_header", True),
                             gyro_dict.get("delimiter", ","),
                             gyro_dict.get("usecols", None),
                             gyro_dict.get("factor", None),
                             gyro_dict.get("function", None))
        self.data_manager.add_data("gyro", gyroscope, gyro_dict.get("units"))

        # read accelerometer
        accelerometer = read_csv(accel_dict.get("filepath"),
                                 accel_dict.get("ignore_header", True),
                                 accel_dict.get("delimiter", ","),
                                 accel_dict.get("usecols", None),
                                 accel_dict.get("factor", None),
                                 accel_dict.get("function", None))
        self.data_manager.add_data("accel", accelerometer, accel_dict.get("units"))

    def run(self):

        # fetch input variables to this algorithm
        input_names = self.algorithm.inputs
        inputs = []

        for _in_name in input_names:
            _in = self.data_manager.get_data(_in_name)
            inputs.append(_in)

        self.algorithm.compute(*inputs)

        # get results and add them to the data manager
        _results = self.algorithm.get_results()
        for _data, _name in zip(_results, self.algorithm.outputs):
            if _data is not None:
                self.data_manager.add_data(_name, _data)

    def results(self, data_dir=None, performance=False, plot=False):
        #### check data dir

        if data_dir is not None:  # data_dir specified, meaning to save .csv files
            data_dir = self._check_data_dir(data_dir)

            # save data files
            self.data_manager.save_data(data_dir)

        INSQualityManager.process(self.data_manager, data_dir, self.algorithm.name, performance, plot)

    def _check_data_dir(self, data_dir):
        """
        check if data_dir is a valid dir. If not, use the default dir.
        check if the data_dir exists. If not, create it.
        Args:
            data_dir: all generated files are saved in data_dir
        Returns:
            data_dir: valid data dir.
        """
        # check data dir
        # data_dir is not specified, automatically create one
        if data_dir == '':
            data_dir = OUTPUT_INS_DIR
            if data_dir[-1] != '//':
                data_dir = data_dir + '//'
            data_dir = data_dir + time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime()) + '//'
            data_dir = os.path.abspath(data_dir)
            print("creating dir ", data_dir)
        # create data dir
        if not os.path.exists(data_dir):
            try:
                data_dir = os.path.abspath(data_dir)
                os.makedirs(data_dir)
            except:
                raise IOError(f"Cannot create dir: {data_dir}")
        return data_dir
