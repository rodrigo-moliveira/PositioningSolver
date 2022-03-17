from collections import OrderedDict
from PositioningSolver.src.data_types.basics.DataType import DataType
from PositioningSolver.src.data_types.basics.Epoch import Epoch
from PositioningSolver.src.gnss.data_types.Satellite import Satellite
from PositioningSolver.src.data_types.containers.TimeSeries import TimeSeries
from PositioningSolver.src.data_types.containers.Container import Container
from PositioningSolver.src.utils.errors import NonExistentObservable, EmptyObservationData
from PositioningSolver.src.gnss.data_types.Observation import Observation


class Header(Container):
    """
    ObservationHeader class, derived from Container
    stores relevant data from the header section of a rinex observation file
    """
    __slots__ = ["rinex_version", "satellite_system", "time_system",
                 "receiver_position", "leap_seconds", "first_epoch", "last_epoch"]

    def __init__(self):
        super().__init__()
        for attr in self.__slots__:
            setattr(self, attr, None)


class EpochData:
    """
    Class EpochData
    Stores all observations for a single epoch. Consists of an Ordered Dict:
        * keys -> satellites
        * items -> Observation objects with the observations for the given epoch
    Attributes
        ----------
        _data : OrderedDict
            The DataType (observation type) of this observation
    """

    def __init__(self):
        self._data = OrderedDict()

    def set_observable(self, satellite: Satellite, observation: Observation):
        """
        method to set a new observation

        Args:
            satellite (Satellite)
            observation (Observation)
        Return:
            bool : true if observation is successfully set. False when this datatype has already been set for
                the given satellite and epoch (no overwriting is performed!)
        """
        if satellite in self._data:
            if observation not in self._data[satellite]:
                self._data[satellite].append(observation)
            else:
                from PositioningSolver.src import get_logger
                log = get_logger("io_manager")
                log.warning(f"Trying to set an observable of type {str(observation)} for satellite {str(satellite)},"
                            f"which has already been set. Overwriting not permitted.")
        else:
            self._data[satellite] = [observation]
        return True

    def get_observables(self, sat: Satellite):
        """
        Args:
                sat (Satellite)
        Return:
                list : list of all observables for the provided satellite (only one epoch)
        """
        return self._data[sat]

    def get_observable(self, sat, obs):
        """
        Args:
            sat (Satellite)
            obs (DataType)
        Return:
            Observation : gets the observation for the provided datatype
        Raises:
            NonExistentObservable
        """
        obs_list = self._data[sat]
        for _obs in obs_list:
            if obs == _obs.datatype:
                return _obs
        raise NonExistentObservable(f"observation {str(obs)} not found for satellite {str(sat)}")

    def has_observable(self, sat, obs):
        obs_list = self._data[sat]
        for _obs in obs_list:
            if obs == _obs.datatype:
                return True
        return False

    def get_satellites(self):
        return list(self._data.keys())

    def get_satellites_for_datatypes(self, *datatype_list):
        sat_list = []

        for sat in self.get_satellites():
            has_type = True  # we assume that this satellite has this type

            # iterate over all requested types
            for datatype in datatype_list:
                if not self.has_observable(sat, datatype):
                    has_type = False  # we found out that actually this satellites does NOT have this type

            # if this satellite has data for all requested datatypes, append to the list
            if has_type:
                sat_list.append(sat)

        return sat_list

    def __str__(self):
        myStr = ""
        for sat, obs in self._data.items():
            myStr += "\t" + str(sat) + " -> " + str(obs) + "\n"

        if myStr == "":
            myStr = "\t-->Empty Epoch Data"

        return myStr

    def remove_observable(self, sat: Satellite, datatype: DataType):
        obs_list = self._data[sat]
        new_obs_list = []

        for obs in obs_list:
            if obs.datatype != datatype:
                new_obs_list.append(obs)
        if new_obs_list:
            self._data[sat] = new_obs_list
        else:
            self._data.pop(sat)

    def remove_for_frequency(self, sat: Satellite, datatype: DataType):
        obs_list = self._data[sat]
        new_obs_list = []

        for obs in obs_list:
            if obs.datatype.freq != datatype.freq:
                new_obs_list.append(obs)
        if new_obs_list:
            self._data[sat] = new_obs_list
        else:
            self._data.pop(sat)

    def remove_satellite(self, sat):
        if sat in self._data:
            self._data.pop(sat)


class ObservationHeader:
    def __init__(self):
        self._header = TimeSeries()

    def __str__(self):
        myStr = "Observation Header:\n" + str(self._header)
        return myStr

    def set_header(self, header: Header):

        if not issubclass(type(header), Header):
            raise TypeError(f'Third argument should be a valid Header object. Type {type(header)} '
                            f'was provided instead')

        self._header.set_data(header.first_epoch, header)


class ObservationData:
    """
    Class ObservationData
    Container that stores all batch observations to be processed in the PVT computation. Consists of an Ordered Dict:
        * keys -> epochs (Epoch objects)
        * items -> EpochData objects
    Attributes
        ----------
        _data : TimeSeries
        """

    def __init__(self):
        self._data = TimeSeries()
        self._types = []
        self._satellites = []

    def __str__(self):
        myStr = "Observation Data:\n"
        for epc, data in self._data.items():
            myStr += str(epc.to_time_stamp()) + "\n"
            myStr += str(data) + "\n"

        return myStr

    def set_observable(self, epoch: Epoch, satellite: Satellite, obsType: DataType, value: float):
        """
        method to set a new observation (read directly from the rinex observation file)

        Args:
            epoch (Epoch) : time at reception of signal (time tag from rinex)
            satellite (Satellite)
            obsType (DataType) : the datatype of the observation
            value (float) : numeric value of the observation
        """

        if not isinstance(epoch, Epoch):
            raise TypeError(f'First argument should be a valid Epoch object. Type {type(epoch)} was provided instead')
        if not isinstance(satellite, Satellite):
            raise TypeError(f'Second argument should be a valid Satellite object. Type {type(satellite)} '
                            f'was provided instead')
        if not isinstance(obsType, DataType):
            raise TypeError(f'Third argument should be a valid DataType object. Type {type(obsType)} '
                            f'was provided instead')
        if not isinstance(value, float) and not isinstance(value, int):
            raise TypeError(f'Forth argument should be a valid number (float or integer). Type {type(value)} '
                            f'was provided instead')

        if isinstance(value, int):
            value = float(value)

        # construct observation
        obs = Observation(obsType, value)

        self.set_observation(epoch, satellite, obs)

    def set_observation(self, epoch: Epoch, satellite: Satellite, obs: Observation):
        if not self._data.has_epoch(epoch):
            # create EpochData object and fill it
            epoch_data = EpochData()
            self._data.set_data(epoch, epoch_data)

        # fetch EpochData object
        epoch_data = self._data[epoch]
        epoch_data.set_observable(satellite, obs)

        # append this obs type to the list
        if obs.datatype not in self._types:
            self._types.append(obs.datatype)

        if satellite not in self._satellites:
            self._satellites.append(satellite)

    def has_type(self, datatype):
        return datatype in self._types

    def has_satellite(self, satellite):
        return satellite in self._satellites

    def remove_observable(self, sat: Satellite, epoch: Epoch, datatype: DataType):
        """
        Remove this observable, for the selected epoch and satellite

         Example: EpochData = [C1, L1, S1, C2, L2, S2]
                remove_observable(datatype = C1)

                -> EpochData = [L1, S1, C2, L2, S2]
        """
        try:
            epoch_data = self._data[epoch]
            epoch_data.remove_observable(sat, datatype)

            # check if there are no satellites (-> remove this epoch_data object)
            if len(epoch_data.get_satellites()) == 0:
                self._data.remove_data(epoch)

        except NonExistentObservable:
            pass

    def remove_for_frequency(self, sat: Satellite, epoch: Epoch, datatype: DataType):
        """
        Remove observations for the selected epoch and satellite which are associated to the frequency
         of the provided datatype.

         Example: EpochData = [C1, L1, S1, C2, L2, S2]
                remove_for_frequency(datatype = C1)

                -> EpochData = [C2, L2, S2]
        """
        try:
            epoch_data = self._data[epoch]
            epoch_data.remove_for_frequency(sat, datatype)
        except NonExistentObservable:
            pass

    # getters
    def get_epoch_data(self, epoch: Epoch):
        """
        Fetch a the EpochData object for this epoch

        Args:
            epoch (Epoch)
        Return:
            EpochData  : epoch data object for this epoch
        Raise:
            NonExistentObservable : if the observations are not found
        """
        try:
            return self._data[epoch]
        except:
            raise NonExistentObservable(f"Non Existent observations for epoch {epoch.to_time_stamp()}")

    def get_observables_at_epoch(self, epoch: Epoch, sat: Satellite):
        """
        Fetch a list of observations for the requested satellite and epoch

        Args:
            sat (Satellite)
            epoch (Epoch)
        Return:
            list : list of observables for the provided sat and epoch
        Raise:
            NonExistentObservable : if the observations are not found
        """

        try:
            return self._data[epoch].get_observables(sat)
        except:
            raise NonExistentObservable(f"Non Existent observation for satellite {str(sat)} "
                                        f"and epoch {epoch.to_time_stamp()}")

    def get_observable_at_epoch(self, sat: Satellite, epoch: Epoch, obs: DataType):
        """
        Fetch the requested observation from the database

        Args:
            sat (Satellite)
            epoch (Epoch)
            obs (DataType)
        Return:
            Observation : the requested observation
        Raises:
            NonExistentObservable : if the observation is not found
        """
        try:
            return self._data[epoch].get_observable(sat, obs)
        except:
            raise NonExistentObservable(f"Non Existent observation for type {str(obs)}, satellite {str(sat)} "
                                        f"and epoch {epoch.to_time_stamp()}")

    def get_epochs(self):
        return self._data.get_all_epochs()

    def get_satellites(self):
        return self._satellites

    def get_types(self):
        return self._types

    def get_satellite_list(self):
        return [str(sat) for sat in self._satellites]

    def get_rate(self):
        epochs = self.get_epochs()
        if len(epochs) > 2:
            return epochs[1] - epochs[0]
        raise EmptyObservationData(f"Observation Data is empty")

    def get_first_arc_epoch(self, sat, epoch, rate):
        """Return the first epoch of the arc, given the provided rate
        """
        while True:
            try:
                self.get_observables_at_epoch(epoch, sat)
                epoch = epoch + (-rate)

            except:
                return epoch + rate
