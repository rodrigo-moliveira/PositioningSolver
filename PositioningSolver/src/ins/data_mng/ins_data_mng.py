from PositioningSolver.src.data_types.containers.Container import Container
from PositioningSolver.src.ins.data_mng.data_sim import SimulatedData


# ref variables:
#   time
#   ref_pos. Reference position in navigation frame n (NED). Form is LLD (latitude, longitude, down)
#   ref_vel. Reference velocity in navigation frame n. Velocity components in NED
#   ref_att. Reference attitude (euler angles in zyx rotation). However, we store them in xyz order,
#           that is roll(x), pitch(y) and yaw(z)

# gps position and velocity are computed in ecef. Position is stored in LLD and velocity in NED components


class InsDataManager(Container):
    __slots__ = ["time", "ref_pos", "ref_vel", "ref_att", "ref_gyro", "ref_accel",
                 "pos", "vel", "att", "gyro", "accel", "gps", "gps_ecef",
                 "_available", "_do_not_save"]

    def __init__(self):
        super().__init__()

        ########################
        # Input PVAT Variables #
        ########################

        # Reference time
        self.time = SimulatedData(name="time", description="sample time", units=["s"], legend=["time"])

        # Reference Position
        self.ref_pos = SimulatedData(name="ref_pos",
                                     description="true position in the navigation frame (NED), in LLD form",
                                     units=['rad', 'rad', 'm'], output_units=['deg', 'deg', 'm'],
                                     legend=['ref_pos_lat', 'ref_pos_lon', 'ref_pos_down'])

        # Reference Velocity
        self.ref_vel = SimulatedData(name='ref_vel', description='true velocity in the navigation frame (NED)',
                                     units=['m/s', 'm/s', 'm/s'],
                                     legend=['ref_vel_N', 'ref_vel_E', 'ref_vel_D'])

        # Reference Attitude
        self.ref_att = SimulatedData(name='ref_att', description='true attitude (Euler angles, ZYX convention)',
                                     units=['rad', 'rad', 'rad'],
                                     output_units=['deg', 'deg', 'deg'],
                                     legend=['ref_Roll', 'ref_Pitch', 'ref_Yaw'])

        #######################
        # Sensor Measurements #
        #######################

        # True (errorless) gyro readout measurements
        self.ref_gyro = SimulatedData(name='ref_gyro',
                                      description='true angular velocity in the body frame (w_ib_b)',
                                      units=['rad/s', 'rad/s', 'rad/s'],
                                      output_units=['deg/s', 'deg/s', 'deg/s'],
                                      legend=['ref_gyro_x', 'ref_gyro_y', 'ref_gyro_z'],
                                      ignore_first_row=True)

        # True (errorless) accelerometer readout measurements
        self.ref_accel = SimulatedData(name='ref_accel',
                                       description='true acceleration in the body frame (f_ib_b)',
                                       units=['m/s^2', 'm/s^2', 'm/s^2'],
                                       legend=['ref_accel_x', 'ref_accel_y', 'ref_accel_z'],
                                       ignore_first_row=True)

        # Real (with error) gyro readout measurements
        self.gyro = SimulatedData(name='gyro',
                                  description='gyro measurements w_ib_b',
                                  units=['rad/s', 'rad/s', 'rad/s'],
                                  output_units=['deg/s', 'deg/s', 'deg/s'],
                                  legend=['gyro_x', 'gyro_y', 'gyro_z'],
                                  ignore_first_row=True)

        # Real (with error) accelerometer readout measurements
        self.accel = SimulatedData(name='accel',
                                   description='accelerometer measurements f_ib_b',
                                   units=['m/s^2', 'm/s^2', 'm/s^2'],
                                   legend=['accel_x', 'accel_y', 'accel_z'],
                                   ignore_first_row=True)

        # Real (with error) GPS measurements
        self.gps = SimulatedData(name='gps',
                                 description='GPS LLD position and NED velocity measurements',
                                 units=['rad', 'rad', 'm', 'm/s', 'm/s', 'm/s'],
                                 output_units=['deg', 'deg', 'm', 'm/s', 'm/s', 'm/s'],
                                 legend=['gps_lat', 'gps_lon', 'gps_down',
                                         'gps_vN', 'gps_vE', 'gps_vD'],
                                 ignore_first_row=True)

        # ECEF GPS measurements
        self.gps_ecef = SimulatedData(name='gps_ecef',
                                      description='GPS ECEF position and ECEF velocity measurements (v_eb_e)',
                                      units=['m', 'm', 'm', 'm/s', 'm/s', 'm/s'],
                                      output_units=['m', 'm', 'm', 'm/s', 'm/s', 'm/s'],
                                      legend=['gps_ecef_x', 'gps_ecef_y', 'gps_ecef_z',
                                              'gps_vx', 'gps_vy', 'gps_vz'],
                                      ignore_first_row=True)

        ################################
        # Computed Position & Velocity #
        ################################

        # Computed Position
        self.pos = SimulatedData(name="pos",
                                 description="computed position in the navigation frame (NED), in LLD form",
                                 units=['rad', 'rad', 'm'], output_units=['deg', 'deg', 'm'],
                                 legend=['pos_lat', 'pos_lon', 'pos_down'])

        # Computed Velocity
        self.vel = SimulatedData(name='vel', description='computed velocity in the navigation frame (NED)',
                                 units=['m/s', 'm/s', 'm/s'],
                                 legend=['vel_N', 'vel_E', 'vel_D'])

        # Computed Attitude
        self.att = SimulatedData(name='att', description='computed attitude (Euler angles, ZYX convention)',
                                 units=['rad', 'rad', 'rad'],
                                 output_units=['deg', 'deg', 'deg'],
                                 legend=['Roll', 'Pitch', 'Yaw'])

        # available data for the current simulation
        self._available = []

        # SimulatedData which is not intended to be saved
        self._do_not_save = ["time"]  # TODO after code is validated, put the reference PVAT here

    def __str__(self):
        return f'{type(self).__name__}( DataManager for INS algorithms )'

    def __repr__(self):
        return str(self)

    def add_data(self, data_name, data, units=None):
        """
        Add data to available.
        Args:
            data_name: data name, str
            data: a scalar, a numpy array or a dict of the above two. If data is a dict, each
                value in it should be of same type (scalar or numpy array), same size and same
                units.
            units: Units of the data. If you know clearly no units convertion is needed, set
                units to None. If you do not know what units are used in the class InsDataMgr,
                you'd better provide the units of the data. Units convertion will be done
                automatically.
                If data is a scalar, units should be a list of one string to define its unit.
                If data is a numpy of size(m,n), units should be a list of n strings
                to define the units.
        """
        if data_name in self.__slots__:
            sim = getattr(self, data_name, None)
            if sim is not None:
                sim.add_data(data, units)

                # add to 'available' list
                if data_name not in self._available:
                    self._available.append(data_name)
        else:
            raise ValueError(f"Unsupported data: {data_name}, not in {self.__slots__}")

    def get_data(self, data_names):
        """
        Get data section of data_names.
        Args:
            data_names: a list of data names
        Returns:
            data: a list of data corresponding to data_names.
            If there is any unavailable data in data_names, return None
        """
        # single data
        if isinstance(data_names, str):
            if data_names in self._available:
                return getattr(self, data_names).data
            else:
                raise ValueError(f'{data_names} is not available.')

        # vector data
        data = []
        for i in data_names:
            if i in self._available:
                data.append(getattr(self, i).data)
            else:
                raise ValueError(f'{i} is not available.')
        return data

    def save_data(self, directory):
        for sim_data in self._available:
            if sim_data not in self._do_not_save:

                # fetch sim_data
                sim = getattr(self, sim_data, None)

                if sim is not None:
                    # print("saving", sim_data)
                    sim.save_to_file(directory, self.time)
